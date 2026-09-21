# 我的 Agent Skills

个人维护的 AI 助手 Skill 集合。按用途分类，在这里统一查找和更新。

## 分类目录

| 分类 | Skill | 当前版本 | 用途 |
| --- | --- | --- | --- |
| 互动叙事 | [复杂酒馆 / Complex Tavern](skills/complex-tavern/SKILL.md) | 3.6.6 | 纯文字互动故事、持续世界与长篇小说 |
| 工作流程 | [不着急 / No-Rush](skills/no-rush/SKILL.md) | 2.5.0 | 默认预加载、需求澄清、任务跟踪与交付检查 |
| 饮食记录 | [duty-NRV / Cut Coach / 减脂教练](skills/cut-coach/SKILL.md) | 1.3.0 | 低成本饮食记录、主动减脂干预、运动配合与趋势审计 |

## 如何使用

打开所需 Skill 的链接，将文件内容交给支持自定义指令或 Skill 的 AI 助手；具体安装方式取决于所用客户端。把文件上传到 GitHub 本身不代表已经安装或启用。

**No-Rush 是特殊的默认控制层。** 若希望“不提到不着急也会运行”，宿主/客户端必须把它加入默认 preload / preflight；仅把 `SKILL.md` 放在 GitHub 无法让一个尚未加载的 Skill 自行启动。具体见 `skills/no-rush/HOST-INTEGRATION.md`。

需要直接读取文件时使用以下地址：

- [复杂酒馆原始文件](https://raw.githubusercontent.com/1948666760dty-sys/agent-skills/main/skills/complex-tavern/SKILL.md)
- [不着急原始文件](https://raw.githubusercontent.com/1948666760dty-sys/agent-skills/main/skills/no-rush/SKILL.md)
- [duty-NRV / Cut Coach / 减脂教练原始文件](https://raw.githubusercontent.com/1948666760dty-sys/agent-skills/main/skills/cut-coach/SKILL.md)

触发规则、加载说明及已有评估记录见 [详细索引](skills/README.md)。减脂教练内含作者的个人目标，使用时请根据自己的情况调整。

## 目录与维护

每个 Skill 固定放在 `skills/<名称>/SKILL.md`；相关脚本、参考资料与评估记录放在同一个 Skill 目录下。分类集中维护在本页，不因调整分类而反复移动 Skill 路径。

- 新增 Skill：建立独立目录，并在本页补充分类、用途和版本。
- 更新 Skill：同步文件中的版本与本页、详细索引中的版本。
- `evals/` 存放已有评估材料；历史结果不代表本次迁移重新执行过评估。
- 本仓库是正式维护地址，游戏项目独立放在 [孤锋演训 / Solo Breach](https://github.com/1948666760dty-sys/solo-breach)。

## 迁移记录

2026-09-21 从 `solo-breach/skills` 拆出。保留了该目录的 40 条历史提交记录；提取目录时提交标识会改变，原始历史仍保留在游戏仓库。

迁移来源提交：[`8ff9714`](https://github.com/1948666760dty-sys/solo-breach/commit/8ff9714edaf438eed6d654a5f0d175ab475183bc)。本次仅整理目录、更新主源地址和索引，没有修改三个 Skill 的功能规则或提升版本号。

旧仓库对应路径保留迁移指引。GitHub 普通文件不支持自动重定向；已有收藏、固定读取地址或安装配置应改为本仓库的新链接。
