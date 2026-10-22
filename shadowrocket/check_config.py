"""只读检查配置、公开规则 URL 和域名优先级；不替代 Shadowrocket 编译/真机测试。"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import urllib.request


ROOT = Path(__file__).resolve().parent
OWN_RULE_BASE = "https://raw.githubusercontent.com/xuzedu/nick-rules/main/shadowrocket/rules/"
BUILTINS = {"DIRECT", "PROXY", "REJECT"}
SUPPORTED = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6",
             "IP-ASN", "USER-AGENT", "URL-REGEX"}
# 这些用例检查不同规则集重叠时的结果，并非站点连通性检查。
CASES = {
    "api.anthropic.com": "Claude", "claude.ai": "Claude", "claude.com": "Claude",
    "clau.de": "Claude", "claude.dev": "Claude", "files.claudeusercontent.com": "Claude",
    "claudemcpclient.com": "Claude", "claudemcpcontent.com": "Claude",
    "modelcontextprotocol.io": "Claude", "api.openai.com": "ChatGPT",
    "chatgpt.com": "ChatGPT", "cdn.oaistatic.com": "ChatGPT",
    "files.oaiusercontent.com": "ChatGPT", "sora.com": "ChatGPT", "chat.com": "ChatGPT",
    "gemini.google.com": "Gemini", "aistudio.google.com": "Gemini",
    "generativelanguage.googleapis.com": "Gemini", "notebooklm.google.com": "Gemini",
    "antigravity.google": "Gemini", "flow.google": "Gemini", "ai.google.dev": "Gemini",
    "grok.x.com": "AI", "grok.com": "AI", "x.ai": "AI", "api.cursor.com": "AI",
    "api.githubcopilot.com": "AI", "windsurf.com": "AI", "perplexity.ai": "AI",
    "openrouter.ai": "AI", "huggingface.co": "AI",
    "x.com": "Twitter", "api.x.com": "Twitter", "api.twitter.com": "Twitter",
    "pbs.twimg.com": "Twitter", "video.twimg.com": "Twitter", "t.co": "Twitter",
    "tweetdeck.com": "Twitter", "www.paypal.com": "PayPal", "paypal.cn": "PayPal",
    "paypal.me": "PayPal", "www.paypalobjects.com": "PayPal",
    "payments.braintree-api.com": "PayPal", "api.braintreegateway.com": "PayPal",
    "venmo.com": "PayPal", "xoom.com": "PayPal",
    "api.stripe.com": "CC出口", "challenges.cloudflare.com": "CC出口",
    "withpersona.com": "CC出口", "hcaptcha.com": "CC出口", "sentry.io": "CC出口",
    "segment.io": "CC出口", "browser-intake-datadoghq.com": "CC出口",
    "ipv4.webshare.io": "CC出口", "accounts.google.com": "谷歌服务",
    "recaptcha.net": "谷歌服务", "gmail.com": "谷歌服务",
    "youtube.com": "YouTube", "rr1.googlevideo.com": "YouTube",
    "netflix.com": "Netflix", "disneyplus.com": "Disney+", "max.com": "Max",
    "open.spotify.com": "Spotify", "t.me": "Telegram", "tiktok.com": "TikTok",
    "facebook.com": "Facebook", "www.amazon.com": "Amazon", "bilibili.com": "哔哩哔哩",
    "github.com": "开发服务", "www.apple.com": "苹果服务",
    "www.baidu.com": "DIRECT", "router.home.arpa": "DIRECT",
    "google-analytics.com": "广告拦截",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def active_lines(text):
    return [s.strip() for s in text.splitlines()
            if s.strip() and not s.lstrip().startswith(("#", ";", "//"))]


def read_sections(text):
    sections, section = {}, None
    for line in active_lines(text):
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            require(section not in sections, f"重复配置段: {section}")
            sections[section] = []
        else:
            require(section is not None, "存在无归属配置行")
            sections[section].append(line)
    return sections


def fetch(url, local_rules=None):
    require(url.startswith("https://raw.githubusercontent.com/"), f"非预期公开源: {url}")
    for attempt in range(3):
        try:
            source = "https"
            if local_rules and url.startswith(OWN_RULE_BASE):
                name = url[len(OWN_RULE_BASE):]
                require(re.fullmatch(r"[A-Za-z0-9_-]+\.list", name), f"规则文件名不合法: {name}")
                data = (local_rules / name).read_bytes()
                source = "local"
            else:
                # 不发送认证头；使用系统正常 HTTPS 证书校验。
                with urllib.request.urlopen(url, timeout=30) as response:
                    data = response.read()
            text = data.decode("utf-8-sig")
            lines = active_lines(text)
            require(lines and "<html" not in text.lower(), f"规则集为空或返回 HTML: {url}")
            rules = []
            for line in lines:
                fields = [f.strip() for f in line.split(",")]
                kind = fields[0]
                require(kind in SUPPORTED, f"未确认的规则类型: {url}: {line}")
                require(len(fields) in (2, 3) and bool(fields[1]), f"规则字段错误: {url}: {line}")
                if len(fields) == 3:
                    require(fields[2] == "no-resolve", f"规则含策略或未知参数: {url}: {line}")
                if kind in {"IP-CIDR", "IP-CIDR6"}:
                    ipaddress.ip_network(fields[1], strict=False)
                if kind == "IP-ASN":
                    require(fields[1].isdigit(), f"ASN 格式错误: {line}")
                rules.append(fields)
            return url, rules, {"url": url, "rules": len(rules),
                                "sha256": hashlib.sha256(data).hexdigest(),
                                "types": dict(Counter(r[0] for r in rules)),
                                "attempts": attempt + 1, "source": source}
        except (OSError, ValueError):
            if attempt == 2:
                raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "NickPro_cn.conf",
                        help="待检查的配置，默认使用脚本旁的 NickPro_cn.conf")
    parser.add_argument("--report", type=Path, help="可选：写入本次检查的 JSON 报告")
    parser.add_argument("--local-rules", type=Path,
                        help="发布前从指定目录读取本仓库 Shadowrocket 规则，上游仍从 HTTPS 获取")
    parser.add_argument("--compare-config", type=Path,
                        help="可选：与拆分前配置对比完整规则展开顺序及分组定义")
    args = parser.parse_args()
    config = args.config
    data = config.read_bytes()
    sections = read_sections(data.decode("utf-8-sig"))
    groups = {}
    for line in sections["Proxy Group"]:
        name, value = map(str.strip, line.split("=", 1))
        require(name not in groups, f"重复分组: {name}")
        groups[name] = [s.strip() for s in value.split(",")]
    edges = {}
    for name, values in groups.items():
        require(values[0] in {"select", "url-test"}, f"未预期的分组类型: {name}")
        refs = [s for s in values[1:] if "=" not in s]
        options = dict(s.split("=", 1) for s in values[1:] if "=" in s)
        require(all(r in groups or r in BUILTINS for r in refs), f"分组引用不存在: {name}")
        regex = options.get("policy-regex-filter")
        if regex:
            re.compile(regex)
        selected = options.get("policy-select-name")
        if selected:
            require(selected in refs or (regex and re.search(regex, selected)),
                    f"默认策略不在成员/筛选中: {name}: {selected}")
        edges[name] = [r for r in refs if r in groups]

    def walk(name, trail):
        require(name not in trail, f"分组循环: {trail + [name]}")
        for child in edges[name]:
            walk(child, trail + [name])

    for name in groups:
        walk(name, [])
    for name in ("CC出口", "Claude", "ChatGPT", "Gemini", "AI", "Twitter", "PayPal", "美国节点"):
        require(groups[name][0] == "select", f"敏感业务不是手动选择: {name}")

    rules = [[s.strip() for s in line.split(",")] for line in sections["Rule"]]
    require(rules[-1] == ["FINAL", "漏网之鱼"], "最终兜底错误")
    require(sum(r[0] == "FINAL" for r in rules) == 1, "存在多个 FINAL")
    for rule in rules:
        require(rule[0] in SUPPORTED | {"RULE-SET", "GEOIP", "FINAL"}, f"未知本地规则: {rule}")
        policy = rule[1] if rule[0] == "FINAL" else rule[2]
        require(policy in groups or policy in BUILTINS, f"规则引用不存在: {rule}")
    require(sections["Proxy"] == [], "新配置不应包含节点凭据")
    require(sections["MITM"] == ["enable = false"], "新配置不应启用解密或携带证书")
    updates = [s for s in sections["General"] if s.startswith("update-url")]
    require(not updates, "拆分版不应包含整份配置的 update-url")
    require(all(r[0] in {"RULE-SET", "GEOIP", "FINAL"} for r in rules),
            "域名/IP 规则应放在独立规则集内")
    urls = list(dict.fromkeys(r[1] for r in rules if r[0] == "RULE-SET"))
    require(not any("/clash/" in u for u in urls), "Shadowrocket 不应再依赖 Clash 源文件")
    baseline = None
    all_urls = urls[:]
    if args.compare_config:
        baseline = read_sections(args.compare_config.read_text(encoding="utf-8-sig"))
        all_urls += [s.split(",")[1] for s in baseline["Rule"] if s.startswith("RULE-SET,")]
        all_urls = list(dict.fromkeys(all_urls))
    print(f"本地结构通过：{len(groups)} 个分组；校验 {len(urls)} 个规则源，发布前本地替代={bool(args.local_rules)}。", flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda u: fetch(u, args.local_rules), all_urls))
    sources = {url: rows for url, rows, _ in results}

    def expand_all(rows):
        output = []
        for r in rows:
            if r[0] == "RULE-SET":
                output.extend([v[0], v[1], r[2], *v[2:]] for v in sources[r[1]])
            else:
                output.append(r)
        return output

    comparison = None
    if baseline:
        baseline_rules = [[s.strip() for s in line.split(",")] for line in baseline["Rule"]]
        old_expanded, new_expanded = expand_all(baseline_rules), expand_all(rules)
        require(old_expanded == new_expanded, "拆分前后完整规则顺序/策略/参数不同")
        require(baseline["Proxy Group"] == sections["Proxy Group"], "拆分改变了分组定义")
        comparison = {"expanded_rules": len(new_expanded), "identical_order_and_policies": True,
                      "proxy_groups_unchanged": True}
    expanded = []
    for rule in rules:
        if rule[0] == "RULE-SET":
            expanded.extend((r[0], r[1], rule[2]) for r in sources[rule[1]])
        elif rule[0].startswith("DOMAIN"):
            expanded.append(tuple(rule[:3]))

    def match(host):
        for kind, value, policy in expanded:
            value = value.lower()
            if ((kind == "DOMAIN" and host == value)
                    or (kind == "DOMAIN-SUFFIX" and (host == value or host.endswith("." + value)))
                    or (kind == "DOMAIN-KEYWORD" and value in host)):
                return policy
        return None

    checks = [{"domain": domain, "expected": expected, "actual": match(domain)}
              for domain, expected in CASES.items()]
    failed = [r for r in checks if r["actual"] != r["expected"]]
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "config_sha256": hashlib.sha256(data).hexdigest(), "groups": len(groups),
              "local_rules": len(rules), "sources": [r[2] for r in results if r[0] in urls],
              "comparison": comparison,
              "domain_checks": checks, "failures": failed,
              "scope": "结构、URL、文本规则语法、域名顺序模拟；未运行 Shadowrocket，未模拟 DNS/IP/ASN/GeoIP/UA/URL 解密规则或模块优先级。"}
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    require(not failed, f"域名分流不符: {failed}")
    print(f"通过：{len(urls)} 个规则源；{sum(len(sources[u]) for u in urls)} 条规则；{len(checks)} 个域名用例。")
    if comparison:
        print(f"拆分等价：{comparison['expanded_rules']} 条展开规则及其顺序、策略、参数完全一致；分组未变。")
    print(report["scope"])


if __name__ == "__main__":
    main()
