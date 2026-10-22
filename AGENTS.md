# nick-rules 维护规则

- 按工具组织规则：clash/ 维护 Clash 规则，shadowrocket/ 维护 Shadowrocket 分流模板，两者独立维护。
- Clash 的权威源文件是 clash/rules/*.list，生成物在 release 分支，禁止手改生成物。
- Clash 不保存完整客户端配置；按用户明确要求，shadowrocket/ 可保存不含节点凭据的完整分流模板。任何目录均不得保存节点地址、账号密码、订阅链接、令牌、HTTPS 解密证书私钥或个人运行日志。
- 保持各客户端已有分类和规则顺序；不要擅自放行前置广告/跟踪拦截或扩大匹配范围。Shadowrocket 已明确的 AI 配套优先顺序见其 README；不得将此顺序变更传播至 Clash。
- 修改 Clash 后运行 scripts/build.py 完成编译和内核配置检查，不堆叠测试。仅修改 Shadowrocket 时运行 python3 shadowrocket/check_config.py；发布使用 main/shadowrocket 的原始文件，不修改 Clash 构建脚本或 release/clash。
- Shadowrocket 自有规则仅维护 shadowrocket/rules/*.list，不引用或修改 clash/rules/。列表不写策略、节点、订阅或嵌套 RULE-SET；策略绑定与节点选择留在客户端配置。模板不设整份 update-url。拆分/重排时校验完整规则展开顺序，不能只抽查域名。
- 发布前确认修改范围；不自动启用或重载用户的 ClashMac 配置。
- 在 /Volumes/SamsungData 下写入前确认外置盘仍挂载；缺失时停止。

