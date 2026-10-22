# Clash 与 Mihomo 规则

`rules/*.list` 是五个独立维护文件，使用不带出口目标的经典规则语法。构建脚本输出可订阅的规则集合。

## 更新地址

| 集合 | behavior / format | 链接 |
| --- | --- | --- |
| NickClaude | classical / yaml | [Claude.yaml](https://github.com/xuzedu/nick-rules/raw/release/clash/classical/Claude.yaml) |
| NickPayment | domain / mrs | [Payment.mrs](https://github.com/xuzedu/nick-rules/raw/release/clash/domain/Payment.mrs) |
| NickTelemetry | domain / mrs | [Telemetry.mrs](https://github.com/xuzedu/nick-rules/raw/release/clash/domain/Telemetry.mrs) |
| NickGoogle | domain / mrs | [Google.mrs](https://github.com/xuzedu/nick-rules/raw/release/clash/domain/Google.mrs) |
| NickExitCheck | domain / mrs | [ExitCheck.mrs](https://github.com/xuzedu/nick-rules/raw/release/clash/domain/ExitCheck.mrs) |

URL 指向 `release` 分支。首次 Actions 成功后链接才可用。生成物还包括可读文本、各类别的完整 classical YAML 和 [构建清单](https://github.com/xuzedu/nick-rules/raw/release/clash/manifest.json)。

## Claude 为什么默认使用 YAML

Claude 源文件同时包含 7 个域名后缀、1 个 IP 网段和 1 个 ASN。MRS 仅支持 domain 或 ipcidr，不支持把 ASN 和域名装进同一个 MRS。

因此默认使用完整的 classical YAML，保留全部 9 条规则。额外提供 [Claude.mrs](https://github.com/xuzedu/nick-rules/raw/release/clash/domain/Claude.mrs)，但它只包含 7 条域名规则；不能直接替换完整集合。`clash/ipcidr/Claude.mrs` 也仅包含网段，不包含 ASN。

## 合并到客户端

参考 [providers.yaml](examples/providers.yaml)。该文件只是合并片段，不能作为完整订阅覆盖配置。

1. 把 `rule-providers` 中的五个条目追加到已有提供者字典，保留其他提供者。
2. 在原广告/跟踪拦截、内网直连之后插入五条 `RULE-SET`，顺序保持 Claude、Payment、Telemetry、Google、ExitCheck。
3. 用这五条引用替换对应的内联规则；其余分流顺序不变。
4. 示例的目标策略为“CC出口”，该策略组需在客户端存在。策略组可使用 `include-all: true` 供手动选择节点，源文件不控制策略组成员，实际出口由客户端中的选择决定。
5. 新配置应先校验，再自行决定是否启用；本仓库不操作客户端或重载网络。

原配置中另有 Claude、OpenAI 等上游规则集时，不会因引入本仓库自动删除或改写。保留的旧 Claude 规则仍可能处理本集合未覆盖的域名。

## 扩充规则

支持 `DOMAIN`、`DOMAIN-SUFFIX`、`IP-CIDR`、`IP-CIDR6`、`IP-ASN`。IP 类型可加 `no-resolve`。不要在源文件写策略组名、节点信息或完整代理配置。

纯域名类别默认使用 MRS；如果未来往其中加入 IP/ASN，构建脚本会为该类别改用完整 classical YAML，并更新生成的接入片段。此时需要同步客户端的 behavior、format 和 URL，不能只替换文件内容。

参见 [Mihomo 规则集合格式说明](https://wiki.metacubex.one/config/rule-providers/)。
