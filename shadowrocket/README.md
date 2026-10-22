# Shadowrocket · NickPro

包含 Claude、ChatGPT、Gemini、其他 AI、Twitter、PayPal 及常用服务的分流配置。节点和订阅在 Shadowrocket 首页管理，模板不包含节点地址、密码、订阅或 HTTPS 解密证书。

## 导入链接

复制下面的地址，在 Shadowrocket「配置」页通过 URL 添加：

```text
https://raw.githubusercontent.com/xuzedu/nick-rules/main/shadowrocket/NickPro_cn.conf
```

[配置原始文件](https://raw.githubusercontent.com/xuzedu/nick-rules/main/shadowrocket/NickPro_cn.conf) · [查看源码](NickPro_cn.conf)

首次使用：

1. 确认首页已经有可用节点或订阅。
2. 导入配置后，在「CC出口」和「美国节点」中手动选择实际节点。公开模板不预选个人节点。
3. 对配置执行「使用配置」或「编译配置」，确认「规则集 URL」全部成功加载。
4. 首页「全局路由」选「配置」。如已有 one-exit 等路由模块，检查其优先规则是否覆盖本配置。

## 分组与默认出口

| 分组 | 默认策略 |
| --- | --- |
| Claude、ChatGPT、Gemini、AI | CC出口 |
| 谷歌服务、Twitter | CC出口 |
| PayPal | 美国节点，也可独立改选 CC出口、全球手动或 DIRECT |
| 国外流量 | PROXY，即首页当前节点 |
| 苹果服务、微软服务、哔哩哔哩 | DIRECT |
| 漏网之鱼 | 国外流量 |

CC出口、美国节点、Twitter、PayPal 均使用手动选择，不使用自动测速切换。候选节点按名称筛选，名称不证明所在地或线路类型；筛选不到节点时，需要调整正则或手动添加候选。手动选择不会保证服务商的出口 IP 永远不变。如果使用住宅落地和中转，请在客户端的实际节点中设置「代理通过」。

Grok 的 `grok.x.com` 单独走 AI，优先于 Twitter 的 `x.com`。Twitter 保留主站、图片、视频、短链接等分流。PayPal 保留独立分组，并补充 Braintree API、Venmo、Xoom 等域名。

## 规则来源与顺序

- 主要使用 [666OS/rules release](https://github.com/666OS/rules/tree/release) 的 `mihomo/*.txt` classical 文本。这些文件包含规则类型，已检查可用于本配置的 RULE-SET；不是 MRS、YAML 或 `+.` 域名集。
- 复用本仓库 `main/clash/rules/*.list` 中五类无策略文本，文件内容保持不变；不使用 release 分支的 Clash 专用 MRS 产物。
- 固定出口设计参考 [one-exit](https://github.com/wquguru/one-exit)。没有直接导入其带固定节点名称的模块，也没有照搬针对特定住宅线路的 IPv6 拒绝规则。
- Amazon、BiliBili 保留 [blackmatrix7 的 Shadowrocket 规则](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Shadowrocket)作为补充。

具体 AI、Twitter、PayPal 等规则排在综合分类之前。共享验证码、Stripe、Persona、Intercom、遥测等依赖路由到 CC出口，**其优先级高于广告规则**；例如 `segment.io` 不会被后面的 Tracking 集拒绝。这是此 Shadowrocket 模板的既有行为，不改变 Clash 仍保留的广告优先顺序。

共享域名会影响所有 App 发往这些域名的请求，无法仅凭域名限定到 Claude。Google 列表包含 Google 主站、Gmail、API 和资源域名，因此普通 Google 请求也会走谷歌服务。需要一致出口时，保持各 AI 组和谷歌服务选择 CC出口；如果 PayPal 也需要相同出口，可自行把它改选 CC出口。

## 更新

配置中的 `update-url` 指向上方同一个地址。更新配置可以获取本仓库最新模板；「使用配置/编译配置」用于重新拉取并应用模板引用的远程规则。可在客户端「自动更新」中启用配置更新并允许系统后台 App 刷新，执行时机受 iOS 调度影响。

**整份配置更新可能覆盖在客户端内修改的策略和参数**，更新后请复核节点选择。如果要长期保持私人定制，可保留本地副本并移除其 `update-url`，仅更新远程规则集。

本文件直接从 `main/shadowrocket/` 提供，不需要 Clash 编译，也不使用 release 分支。仅改本目录、根 README 和对应维护约定，不会触发现有 Clash 工作流的路径条件。

## 验证

运行 `python3 shadowrocket/check_config.py`（Python 3，仅标准库）。脚本校验分组引用、循环、规则 URL 和文本语法，并模拟关键域名的匹配顺序。它通过普通 HTTPS 读取公开规则，不读取节点凭据，不激活代理。

本次准备时的检查规模为 38 个分组、37 个远程规则源、73 个域名用例。该检查不是 Shadowrocket 编译器，没有验证实际 DNS、IP/ASN/GeoIP、UA、模块覆盖或登录体验。规则源会变化，结果以每次运行输出为准。

导入后用客户端「测试规则」确认：

| 请求 | 预期分组 |
| --- | --- |
| api.anthropic.com | Claude |
| chatgpt.com | ChatGPT |
| generativelanguage.googleapis.com | Gemini |
| grok.x.com | AI |
| x.com、video.twimg.com | Twitter |
| paypal.com、payments.braintree-api.com | PayPal |
| ipv4.webshare.io | CC出口 |

最后结合连接日志确认实际节点，并实际测试 AI 对话、验证、Twitter 媒体和 PayPal 页面。本模板不需要启用 MITM 或安装解密证书。

[返回仓库入口](../README.md)
