# 原位升级现有 @复杂酒馆：发布门槛与入口绑定手册

**状态：待发布，不影响现有已安装 Skill。**

目标是升级原来的 `@复杂酒馆 / @complex-tavern`，不创建同名新插件或额外 Beta，不改变已安装插件的主体身份、历史关联、默认权限和可用入口；不迁移、读取、覆盖或上传私人剧情/STATE/Raw Story Log。

## 2026-10-14 实际核验

- **旧入口实际内容**：当前已加载的 `skills://plugins/complex-tavern/complex-tavern/skill.md` 仍为 v3.7.1；其 YAML `canonical_repository` 指向 `1948666760dty-sys/agent-skills`，`canonical_path` 指向 `skills/complex-tavern/SKILL.md`，并要求激活时优先验证 GitHub canonical。
- **新规则候选**：PR #8，`skills/complex-tavern-v4-demo/SKILL.md`（保留 demo.6 核心并增加统一适配第 21 节）；新规则的现有 `canonical_path` 仍为 Demo 路径。
- **账户发布入口不明**：已安装 Skill 的 URI 与可编辑插件后端 `plugin_id` 不等价，不能从名称或 `plugin://...` 猜造后端 ID。当前 Plugin Creator 可编辑的个人插件清单没有该旧入口；插件市场搜索也没有给出能核实归属的原插件结果。未确认它是否属于 workspace/Git-managed/其他管理渠道。
- **仓库不是自动安装器**：仓库只有 Skills 规则，没有该 Skill 的原始 `plugin.json` 或 GitHub 到 ChatGPT 插件版本的自动同步工作流。
- **静态/逻辑检测**：候选分支 GitHub Actions 执行统一源检查 31/31 PASS 和原 demo.6 40 项输出逻辑用例；Push/PR 事件成功。并不证明真实 ChatGPT/Muse UI 或长期存档事务通过。

## 不要直接做的事

1. 不要把原 Demo 整份原封不动覆盖稳定目录：Demo 内的 canonical_path、显式 Demo 路由、version/status、存档克隆隔离及版本首行语义，与原 `@` 默认稳定入口不同。
2. 不要把 GitHub PR 合并当作已安装插件更新：分支目录不同，老 `@` 入口仍可能引用旧稳定路径，宿主也可能使用打包副本。
3. 不要用 `create_plugin` 新建同名插件试图“覆盖”旧身份；新建与真正的 update/原位发布不是一回事。
4. 不要把私人 `story-*`、`STATE.md`、存档目录、Raw Story Log、剧情日志、实体实例、用户聊天或成人剧情样例加入公开规则仓库。
5. 不要在未核实真实原插件 ID、当前 release、作用域（personal/workspace）和原 `plugin.json` 的情况下运行 `update_plugin`。

## 原位升级的正确顺序

### A. 宿主身份核验（阻塞）

在 ChatGPT **Plugins → Created by you** 或已安装 `@复杂酒馆` 的详情/编辑入口查看其真实管理来源：

- 如果是 Plugin Creator 管理的个人/工作区插件：取得真正的后端 `plugin_id`、current_release_id 与源文件列表；通过 `get_plugin_files` 和 `update_plugin` 按原身份更新，严格保留原 `plugin.json` 及 `defaultPrompt`、配置、其他 assets。
- 如果是 Git 管理或其他 managed 技能：使用该入口明确显示的更新/同步机制，绝不使用不相干的个人插件更新 API。
- 如果宿主不提供更新权限或身份无法核实：**暂停原位发布**，仍可直接按指定 GitHub 版本在普通聊天中读规则，但不能宣称原 `@` 已升级。

### B. 正式版适配（阻塞）

测试通过后制作单独的正式候选补丁，使 `skills/complex-tavern/SKILL.md` 的入口与新增核心匹配：

- 保留原 @ / Skill 的名字与默认激活方式（明确用户说使用复杂酒馆即可触发）。
- 将 `canonical_repository`、`canonical_path`、version/status 与 visible banner 等统一指向正式稳定文件，不能继续意外跳回 Demo；保留原始版本历史与版本提升规则。
- v4 private namespace 跟旧 v3 存档严格隔离。已存在的私人故事必须经过 **另行明确授权** 才允许克隆或迁移；默认不读取，也不自动续写。
- 正式版 metadata、README 与 `skills/README.md` 的索引/版本应同一个提交一致，不作仓促部分更新。

### C. 发行验证（阻塞）

1. GitHub CI 复跑；新增完整验收覆盖入口版本首行、门控菜单、Action Queue、十轮合成世界、梦境/日期/NPC 权限、不生成假卡片、不伪造持久化；绝不能使用私人剧情做测试。
2. 若宿主原生 UI/卡片缺失则使用文字回退，不声称 Muse 原版十二张 HTML 已实际移植。
3. 先确认已安装插件可原位更新并保留 ID，再发布 GitHub 稳定版与该入口的相应 release，同步版本信息。
4. **在一个新的 ChatGPT 轮次真实使用原来的 `@复杂酒馆` 测试**：验证加载的 canonical 版本、功能、无故事串档；输出证据并区分已验证部分与尚未验证部分。
5. 无法验证任何关键环节都应保留旧 v3.7.1 默认入口，不作假成功声明。

## 本次结论

现阶段 GitHub 候选源码、离线检查已具备；**原 @ 的后端安装身份和编辑能力尚未核实，是原位发布的阻塞项**。保留 PR #8 为 Draft，不合并、不覆盖稳定版、不创建新插件、不触及私人剧情。
