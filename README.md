# nick-rules

个人偏好的网络分流规则，按客户端工具独立组织。当前提供 Clash / Mihomo 规则集和 Shadowrocket 分流配置模板。

Clash 部分只保存公开域名、网段、ASN 和构建代码，出口策略由客户端配置决定。Shadowrocket 部分另提供不含节点凭据的完整分流模板，节点和订阅仍由客户端管理。仓库不保存服务器地址、账号密码、订阅链接、令牌或 HTTPS 解密证书。

## 工具目录

| 工具 | 维护目录 | 发布目录 | 状态 |
| --- | --- | --- | --- |
| Clash / Mihomo | [clash/](clash/README.md) | release 分支 `clash/` | 已实现 |
| Shadowrocket | [shadowrocket/](shadowrocket/README.md) | main 分支 `shadowrocket/rules/*.list` | 本地配置保留节点选择，远程规则独立更新 |

## Clash 的五类规则

| 类别 | 权威源文件 | 初始条数 | 默认更新文件 |
| --- | --- | ---: | --- |
| Claude 与 Anthropic | [Claude.list](clash/rules/Claude.list) | 9 | `clash/classical/Claude.yaml` |
| 支付、身份验证与客服 | [Payment.list](clash/rules/Payment.list) | 8 | `clash/domain/Payment.mrs` |
| 遥测服务 | [Telemetry.list](clash/rules/Telemetry.list) | 6 | `clash/domain/Telemetry.mrs` |
| Google 与验证码 | [Google.list](clash/rules/Google.list) | 6 | `clash/domain/Google.mrs` |
| 出口检查 | [ExitCheck.list](clash/rules/ExitCheck.list) | 1 | `clash/domain/ExitCheck.mrs` |

只修改 `main` 分支的源文件。推送后 Actions 编译和校验，成功才更新 `release` 分支。客户端每 86400 秒拉取一次；无需为了修改域名重新编辑完整代理配置。

## Shadowrocket 配置

[首次导入 NickPro_cn.conf](https://raw.githubusercontent.com/xuzedu/nick-rules/main/shadowrocket/NickPro_cn.conf)

配置包含 AI、Twitter、PayPal 及常用服务分组。个人规则独立保存在 `shadowrocket/rules/*.list`，不再引用 `clash/rules/`；666OS 等上游规则仍直接引用。手机保留本地配置与节点选择，日常只更新规则集，不更新整份模板。旧用户请按 [迁移说明](shadowrocket/README.md#旧配置迁移保留已选节点) 只替换规则段并移除旧 update-url。该目录不经 Clash 的 MRS 编译流程，也不改动 release/clash。

## 维护入口

- [Shadowrocket 接入说明](shadowrocket/README.md)
- [Clash 接入说明](clash/README.md)
- [配置合并片段](clash/examples/providers.yaml)
- [日常维护与发布](CONTRIBUTING.md)
- [构建与发布记录](https://github.com/xuzedu/nick-rules/actions)

Clash 部分维护上述五类规则。Shadowrocket 配置也直接引用 666OS 等上游规则集，没有镜像或接管它们。

## 来源和语义

初始规则依据 [one-exit 的 Clash Party 模板](https://github.com/wquguru/one-exit/blob/main/clash-party/override.yaml)，按个人配置需求整理：不采用宽泛关键词匹配和特定 IPv6 拒绝规则。后续由本仓库独立维护，不自动抓取覆盖上游模板。

Clash 的遥测规则是出口路由，不是放行清单，继续放在现有广告和跟踪拦截规则之后。Shadowrocket 模板沿用用户此次指定的 AI 兼容性顺序，共享验证/遥测依赖位于广告规则之前，详见该目录说明。Google、支付、验证等服务被其他网站共用，按域名匹配会影响所有访问这些目标的应用。

