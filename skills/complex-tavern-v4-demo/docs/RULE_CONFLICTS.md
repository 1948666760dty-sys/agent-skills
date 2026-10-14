# Muse × GPT-6 冲突处理矩阵

| 项目 | 统一裁决 |
|---|---|
| 普通入口 vs Muse 独有命令 | 保留 stable/v4 显式路由，Muse 仅展示配置 |
| GitHub 版本首行 vs GPT-6 省略 | GitHub 加载核验与首行硬闸门保留 |
| Muse 每轮20项 vs Demo 3–6项 | compact 默认，expanded 最多20真实选项；无 Gate 不造菜单 |
| Muse 固定 S/T 性行为选项 | 不移植配额；年龄/同意/内容边界优先 |
| Muse C1=3 C2=4 默认 | 不自动覆盖核心已有 C1/C2 默认；可显式 per-story 设定 |
| Muse 每轮询问 0/1/2 次 | 强制基础 Preflight，额外次数按需配置 |
| Muse 日期每轮完整显示 | 内部时间准确；前台按 daily_anchor/natural/off |
| Muse 固定第二人称 | second_person_limited 作为可选视角 |
| 梦境互通与道具 | 普通梦隔离；明确 World Contract 例外 |
| S数字场景号和 meta 旁白 | 只留后台/审计，不进入正文 |
| 人物身份不明 | 依 Cast Identity 保留 unknown/name_source |
| 体力、电量每回合浮动 | 有因果才变，无因果保持 |
| HTML卡及 embed_token | 仅实际宿主/当轮真实值；不可用回退文本 |
| 地图每轮提供 | 必须有真实 POS/模板；脚本未执行不能声称 PASS |
| 运维三件套 vs Commit Protocol | 增加独立 ops；不改 18.1 的单次提交 |
| 私人剧情与 STATE 上传 | 明确禁止，不参与此候选 |
| YAML frontmatter 曾丢 | main 当前完整；新版本必须保留 |
| 运维更新要不要 bump | 候选不发布，不擅自决定 human/com 号 |
