# nick-rules

个人偏好的网络分流规则，按客户端工具独立组织。当前实现 Clash / Mihomo，后续可在 `shadowrocket/` 等目录维护对应工具的规则。

仓库只保存公开域名、网段、ASN 和构建代码，不保存节点、订阅或客户端完整配置。规则决定匹配哪些请求，出口策略由客户端配置决定。

## 工具目录

| 工具 | 维护目录 | 发布目录 | 状态 |
| --- | --- | --- | --- |
| Clash / Mihomo | [clash/](clash/README.md) | release 分支 `clash/` | 已实现 |
| Shadowrocket 等 | 后续按工具增加独立目录 | 按工具隔离 | 本版未实现 |

## 五类规则

| 类别 | 权威源文件 | 初始条数 | 默认更新文件 |
| --- | --- | ---: | --- |
| Claude 与 Anthropic | [Claude.list](clash/rules/Claude.list) | 9 | `clash/classical/Claude.yaml` |
| 支付、身份验证与客服 | [Payment.list](clash/rules/Payment.list) | 8 | `clash/domain/Payment.mrs` |
| 遥测服务 | [Telemetry.list](clash/rules/Telemetry.list) | 6 | `clash/domain/Telemetry.mrs` |
| Google 与验证码 | [Google.list](clash/rules/Google.list) | 6 | `clash/domain/Google.mrs` |
| 出口检查 | [ExitCheck.list](clash/rules/ExitCheck.list) | 1 | `clash/domain/ExitCheck.mrs` |

只修改 `main` 分支的源文件。推送后 Actions 编译和校验，成功才更新 `release` 分支。客户端每 86400 秒拉取一次；无需为了修改域名重新编辑完整代理配置。

## 维护入口

- [Clash 接入说明](clash/README.md)
- [配置合并片段](clash/examples/providers.yaml)
- [日常维护与发布](CONTRIBUTING.md)
- [构建与发布记录](https://github.com/xuzedu/nick-rules/actions)

本版只迁移上述五类规则。OpenAI 规则集继续由客户端现有配置引用原来源，没有在此仓库镜像或接管。

## 来源和语义

初始规则依据 [one-exit 的 Clash Party 模板](https://github.com/wquguru/one-exit/blob/main/clash-party/override.yaml)，按个人配置需求整理：不采用宽泛关键词匹配和特定 IPv6 拒绝规则。后续由本仓库独立维护，不自动抓取覆盖上游模板。

遥测规则是出口路由，不是放行清单。应放在现有广告和跟踪拦截规则之后。Google、支付、验证等服务被其他网站共用，按域名匹配会影响所有访问这些目标的应用。
