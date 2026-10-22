#!/usr/bin/env python3
"""Compile tool-specific source rules; never read or modify a client profile."""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ('Claude', 'Payment', 'Telemetry', 'Google', 'ExitCheck')
DOMAIN = re.compile(r'(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\Z')


def ensure_mount(path):
    if path.parts[:2] == ('/', 'Volumes'):
        mount = Path(*path.parts[:3])
        if not mount.is_mount():
            raise ValueError(f'External volume is not mounted: {mount}')


def read_rules(path):
    rules = []
    seen = set()
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(',')
        if len(parts) not in (2, 3) or any(p != p.strip() or not p for p in parts):
            raise ValueError(f'{path.name}:{line_number}: invalid rule')
        kind, value = parts[:2]
        if kind in ('DOMAIN', 'DOMAIN-SUFFIX'):
            valid = len(parts) == 2 and DOMAIN.fullmatch(value)
        elif kind in ('IP-CIDR', 'IP-CIDR6'):
            network = ipaddress.ip_network(value, strict=True)
            valid = network.version == (4 if kind == 'IP-CIDR' else 6)
            valid = valid and (len(parts) == 2 or parts[2] == 'no-resolve')
        elif kind == 'IP-ASN':
            valid = value.isdigit() and 0 < int(value) <= 4294967295
            valid = valid and (len(parts) == 2 or parts[2] == 'no-resolve')
        else:
            raise ValueError(f'{path.name}:{line_number}: unsupported type {kind}')
        if not valid or line in seen:
            raise ValueError(f'{path.name}:{line_number}: invalid or duplicate rule')
        seen.add(line)
        rules.append(line)
    if not rules:
        raise ValueError(f'{path.name}: empty rule set')
    return rules


def run(command):
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def emit_yaml(path, rules):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('payload:\n' + ''.join('  - ' + json.dumps(r) + '\n' for r in rules))


def build(mihomo, output, repository):
    ensure_mount(ROOT)
    ensure_mount(output)
    if output.exists():
        raise ValueError('Output already exists; choose a fresh build directory')
    sources = {name: read_rules(ROOT / 'clash/rules' / f'{name}.list') for name in CATEGORIES}
    output.mkdir(parents=True)
    manifest = {'repository': repository, 'compiler': run([mihomo, '-v']).splitlines()[0], 'categories': {}}
    providers = {}
    for name, rules in sources.items():
        classical = Path('clash/classical') / f'{name}.yaml'
        emit_yaml(output / classical, rules)
        domains = []
        cidrs = []
        for rule in rules:
            kind, value, *_ = rule.split(',')
            if kind in ('DOMAIN', 'DOMAIN-SUFFIX'):
                domains.append(('+.' if kind == 'DOMAIN-SUFFIX' else '') + value)
            elif kind in ('IP-CIDR', 'IP-CIDR6'):
                cidrs.append(value)
        artifacts = [classical.as_posix()]
        for behavior, values in [('domain', domains), ('ipcidr', cidrs)]:
            if not values:
                continue
            text_path = output / 'clash' / behavior / f'{name}.txt'
            text_path.parent.mkdir(parents=True, exist_ok=True)
            text_path.write_text('\n'.join(values) + '\n')
            mrs_path = text_path.with_suffix('.mrs')
            run([mihomo, 'convert-ruleset', behavior, 'text', str(text_path), str(mrs_path)])
            if not mrs_path.stat().st_size:
                raise ValueError(f'Empty MRS: {name}')
            artifacts.extend([str(p.relative_to(output)) for p in (text_path, mrs_path)])
        # A mixed set must use classical YAML: MRS cannot encode ASN rules.
        only_domains = len(domains) == len(rules)
        recommended = f'clash/domain/{name}.mrs' if only_domains else classical.as_posix()
        providers['Nick' + name] = {
            'type': 'http', 'behavior': 'domain' if only_domains else 'classical',
            'format': 'mrs' if only_domains else 'yaml', 'interval': 86400,
            'url': f'https://github.com/{repository}/raw/release/{recommended}',
            'path': f'./rules/nick-rules/{name}.' + ('mrs' if only_domains else 'yaml'),
        }
        manifest['categories'][name] = {
            'rules': len(rules), 'domain_rules': len(domains),
            'source_sha256': hashlib.sha256((ROOT / 'clash/rules' / f'{name}.list').read_bytes()).hexdigest(),
            'recommended': recommended,
            'artifacts': {p: hashlib.sha256((output / p).read_bytes()).hexdigest() for p in artifacts},
        }
    examples = output / 'clash/examples'
    examples.mkdir(parents=True)
    # JSON values are valid YAML and avoid needing a third-party YAML dependency.
    example = 'rule-providers:\n' + ''.join(
        f'  {name}: {json.dumps(value, ensure_ascii=False)}\n' for name, value in providers.items())
    example += '\n# Insert after existing advertising/tracking and private-network rules.\n'
    example += '# Keep the rest of your original rules; this is only a merge fragment.\n'
    example += 'rules:\n' + ''.join(f'  - RULE-SET,{name},CC出口\n' for name in providers)
    (examples / 'providers.yaml').write_text(example)
    # Validate all recommended artifacts with a temporary, offline, non-listening config.
    with tempfile.TemporaryDirectory(prefix='nick-rules-check-') as directory:
        home = Path(directory)
        local = {}
        for name, provider in providers.items():
            rel = manifest['categories'][name.removeprefix('Nick')]['recommended']
            target = home / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(output / rel, target)
            local[name] = {'type': 'file', 'behavior': provider['behavior'],
                           'format': provider['format'], 'path': str(target)}
        config = {'mode': 'rule', 'log-level': 'error', 'rule-providers': local,
                  'rules': [f'RULE-SET,{name},DIRECT' for name in providers] + ['MATCH,DIRECT']}
        config_path = home / 'config.json'
        config_path.write_text(json.dumps(config))
        run([mihomo, '-t', '-d', str(home), '-f', str(config_path)])
    (output / 'clash/manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: info['rules'] for name, info in manifest['categories'].items()}))
    print('MRS conversion and offline Mihomo configuration validation passed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mihomo', required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--repository', default='xuzedu/nick-rules')
    args = parser.parse_args()
    if not re.fullmatch(r'[\w.-]+/[\w.-]+', args.repository):
        parser.error('Expected owner/repository')
    build(str(Path(args.mihomo).resolve()), args.output.resolve(), args.repository)
