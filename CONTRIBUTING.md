# 日常维护与发布

## 修改规则

在 `main` 分支编辑对应工具的权威源文件。本版是 `clash/rules/` 下的五个 `.list` 文件，每行一条不带策略目标的规则，`#` 开头为注释。

保持类别边界，新增规则时说明服务用途。不要使用过宽关键词代替已知域名，不要擅自调整客户端原有广告/跟踪拦截优先级。删除规则时直接删除源文件对应行，不编辑 release 分支的生成物。

## 本地编译

使用已安装的 Mihomo，将路径换成实际位置。输出目录必须是尚不存在的目录：

```sh
python3 scripts/build.py --mihomo /absolute/path/to/mihomo --output /tmp/nick-rules-build
```

脚本检查规则语法与重复项、生成 MRS 和 YAML，并通过临时的本地文件规则集执行一次 `mihomo -t`。校验配置不监听代理端口、不读取完整客户端配置，也不激活客户端。

## 发布

```sh
git add clash/rules
git commit -m "Update Clash rules"
git push origin main
```

Actions 固定使用 Mihomo v1.19.33，并验证下载文件 SHA256。构建成功后只更新 release 分支的 `clash/`，为其他工具保留独立发布空间。README 的单独修改不会触发构建；需要时可在 Actions 手动运行工作流。

发布后查看工作流是否成功，再核对 release 中的可读文本和 `clash/manifest.json`。客户端按 interval 更新，不保证推送后立即生效；需要即时同步时使用客户端的规则资源更新功能。

更新编译器版本时，同时核对官方资产名和 SHA256，修改工作流后重新构建。

## 回退

在 main 上用 `git revert` 回退相应源文件提交并推送，再等 Actions 重新发布。不要只回退生成文件，否则下次构建会覆盖。

## 新增工具

Shadowrocket 等工具分别使用 `shadowrocket/` 等目录及独立接入说明。规则语义和模块语法需按目标工具适配，不将 Clash 的 MRS 文件直接当作 Shadowrocket 模块。发布工作流必须限制到自身工具目录，不能清空其他工具的 release 产物。
