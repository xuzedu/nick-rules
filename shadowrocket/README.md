# Shadowrocket · 本地节点选择与远程规则分离

本目录将个人分流内容放在 `rules/*.list`，手机上的配置只保留分组、节点选择和规则集到策略的绑定。日常使用“使用配置／编译配置”更新规则集，不需要重新下载整份配置。

**只更新规则集不会从本仓库改写你的分组或节点选择。** 模板不再包含整份配置的 `update-url`。首页订阅删除/改名节点、手动切换分组等客户端行为仍可能影响实际选择。

## 文件与规则入口

| 要调整的服务 | 自有规则文件 | 手机策略 |
| --- | --- | --- |
| Claude / Anthropic | [rules/Claude.list](rules/Claude.list) | Claude |
| ChatGPT / OpenAI / Sora | [rules/ChatGPT.list](rules/ChatGPT.list) | ChatGPT |
| Gemini / AI Studio / NotebookLM 等 | [rules/Gemini.list](rules/Gemini.list) | Gemini |
| 其他 AI / Grok | [rules/AI.list](rules/AI.list) | AI |
| Twitter / X / 图片视频 / 短链接 | [rules/Twitter.list](rules/Twitter.list) | Twitter |
| PayPal / Braintree / Venmo / Xoom | [rules/PayPal.list](rules/PayPal.list) | PayPal |
| 共享支付、验证码与身份验证 | [rules/Payment.list](rules/Payment.list) | CC出口 |
| 共享遥测 | [rules/Telemetry.list](rules/Telemetry.list) | CC出口 |
| Google 与验证码 | [rules/Google.list](rules/Google.list) | 谷歌服务 |
| 出口检查 | [rules/ExitCheck.list](rules/ExitCheck.list) | CC出口 |
| 本地网络 | [rules/LAN.list](rules/LAN.list) | DIRECT |
| Max 补充 | [rules/Max.list](rules/Max.list) | Max |

这些文件从旧配置和原先引用的五类列表提取，之后与 Clash 独立维护。**不要为了修改小火箭而编辑 `clash/rules/`。** 小火箭现已不再引用它们。

自有列表之外，模板继续直接引用 [666OS/rules release](https://github.com/666OS/rules/tree/release) 的 classical 文本，以及 blackmatrix7 的 Amazon、BiliBili 列表，共 32 个上游规则源。它们仍按各自上游更新；没有复制成不会更新的本地快照。原规则顺序保留。

## 旧配置迁移：保留已选节点

这次需要在手机上做一次迁移，之后日常只更新规则。

1. 在 Shadowrocket 中复制当前已选好节点的配置，保留旧版作备份。对副本进行纯文本编辑。
2. 打开仓库中的 [NickPro_cn.conf](NickPro_cn.conf)，复制其从 `[Rule]` 开始、到下一个 `[Host]` 之前的整个规则段，替换副本中原来的 `[Rule]` 段。
3. **不要替换副本的 `[Proxy Group]`、`[Proxy]` 或其他个人设置。** 新旧分组名称与绑定保持一致。
4. 在副本的 `[General]` 中删除旧的 `update-url = ...` 行，并确认使用的是本地副本；不要再对旧远程配置点“更新配置”。
5. 对副本执行“使用配置／编译配置”，确认 44 个规则源（12 个自有、32 个上游）加载成功。核对 CC出口、美国节点、Twitter、PayPal 的选择，再把全局路由设为“配置”。

这次迁移的分组定义保持原样，但客户端复制配置时是否继承全部运行时选择未做真机验证，所以首次切换副本后需要核对一次。**不要用整份重新导入的模板去覆盖正在使用的私人配置来代替上述步骤。**

原配置维护者说明：[更新配置会覆盖本地修改](https://github.com/lowertop/Shadowrocket#更新配置)；[使用配置会更新并编译远程规则](https://github.com/lowertop/Shadowrocket#使用配置)。[没有 update-url 的本地配置仍可更新远程规则资源](https://github.com/lowertop/Shadowrocket#自动更新)。

## 新用户首次导入

[配置原始文件](https://raw.githubusercontent.com/xuzedu/nick-rules/main/shadowrocket/NickPro_cn.conf) 用于首次建立配置。导入后保留本地副本，并按上述方式确认没有整份 update-url，日常只编译或更新规则集。

节点和订阅继续在首页管理。首次手动选择“CC出口”和“美国节点”，然后：
- Claude、ChatGPT、Gemini、AI、谷歌服务、Twitter 默认选择 CC出口。
- PayPal 默认选择美国节点，可在手机上独立改选。
- 手动选择不等于服务商保证固定 IP，候选节点名称也不证明线路属性。

## 以后如何改规则

在 main 分支修改上表对应列表，一行一条规则，不写策略名称。例如：

```text
DOMAIN-SUFFIX,new-service.example
DOMAIN,api.another-service.example
IP-CIDR,192.0.2.0/24,no-resolve
```

以上是语法示例，不应原样加入实际列表。不要使用 Clash 的 `payload:`、MRS、YAML，不要在列表内嵌套 RULE-SET。具体策略由手机配置的 RULE-SET 行决定。

提交后，在手机当前本地配置上执行“使用配置／编译配置”。也可启用客户端的配置后台更新、允许系统后台 App 刷新；无更新地址的本地配置只更新规则资源，实际时间受 iOS 调度影响。GitHub 原始文件缓存可能导致变更不是立即可见，可稍后重试并查看规则集预览。

**边界：** 此方式适合增删域名/网段，不能远程创建新分组或改变规则集绑定到哪个策略。需要改节点时在手机上操作；需要新增分组或调整 RULE-SET 顺序时，需另行更新手机配置中的对应部分。已有域名也可能被更早的其他列表或上游命中，不能仅在后面的列表加一行就保证覆盖；修改后应使用检查脚本及客户端“测试规则”核对。

## 分流行为保持不变

具体 AI 服务优先于 Google、开发服务和综合 AI；`grok.x.com` 走 AI，而普通 `x.com` 走 Twitter。PayPal 保留独立分组。共享验证、支付和遥测仍优先于广告拦截，全部 App 发往这些共享域名的请求都会受影响。Clash 的广告优先顺序不受影响。

配置不包含节点地址、密码、订阅、令牌或 HTTPS 解密证书，不启用 MITM。固定出口设计参考 [one-exit](https://github.com/wquguru/one-exit)，没有直接导入其固定节点名称模块。

## 检查与发布

只改本目录以及必要的根说明，不改 Clash 文件、构建脚本、工作流和 release 分支。规则直接由 main 分支提供，不需要 Actions 编译。

本地修改后，使用 Python 3 标准库检查：
```sh
python3 shadowrocket/check_config.py --local-rules shadowrocket/rules
```

发布后检查实际远程资源：
```sh
python3 shadowrocket/check_config.py
```

拆分时还运行了 `--compare-config 拆分前配置.conf`，在同一批上游内容下逐条对比完整展开结果（包括策略、IP 参数和顺序），并比较分组定义。本次准备检查通过：38 个分组、12 个自有列表、32 个上游源、73 个域名用例；160,077 条展开规则与原配置完全一致。

检查是文本和规则顺序验证，不是 Shadowrocket 编译器，不证明实际节点出口、IP/ASN/GeoIP 运行时判断或登录体验。首次迁移仍需在手机上检查日志和实际访问。

[返回仓库入口](../README.md)
