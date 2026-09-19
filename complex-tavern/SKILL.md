---
name: complex-tavern-engine-v3
display_name: 复杂酒馆
description: 通用、纯文字、长局持续世界互动叙事与自动长篇小说引擎。v3.6.4 在 v3.6.3 Novel Output Contract Gate 基础上新增 Visible Output Semantics Lock：凡会改变用户最终/中间可见内容、批次是否暂停、Word 如何持续更新或何时交付的字段，都必须显式解析或由用户明确措辞可靠推导；禁止 silent default 隐藏自动选择、把批次擅自变成停顿、提前交付用户只要求最终版的 Word，或在最终导出时强制退回 Novel Edition。继续保留 v3.6.2 Narrative Release Gate、v3.6.1 长篇运行/记忆生命周期以及既有分支、交互审计与 source-first 开局规则。
version: 3.6.4
status: stable-default
canonical_repository: 1948666760dty-sys/solo-breach
canonical_path: skills/complex-tavern/SKILL.md
activation: default-on-trigger
---

# Complex Tavern Engine v3.6.4 — Visible Output Semantics Lock

## 0. 性质与真实性边界

这是供语言模型执行的玩法规范，不是独立可执行程序，也不代表已作为 ChatGPT 原生 Skill 安装。核心规则全部包含在本文件中，不依赖外部仓库、图片模型、脚本、插件或其他 Skill 才能运行。

### 0.1 规范主源与默认加载

复杂酒馆的规范主源（canonical）固定为：
- Repo: `1948666760dty-sys/solo-breach`
- Path: `skills/complex-tavern/SKILL.md`

默认加载规则：
- 当用户表达“开始复杂酒馆 / 继续复杂酒馆 / 按复杂酒馆玩 / 使用复杂酒馆”等明确触发语义，且未指定旧版本时，默认使用 GitHub canonical 的最新正式版本。
- GitHub 可访问时，启用前优先读取 canonical 文件；Library / 本地副本只作为 fallback。
- GitHub 与 Library / 本地版本不一致时，以 GitHub canonical 为准。
- GitHub 暂时不可访问时，可以使用 Library / 本地 fallback，但不得声称已经验证为 GitHub 最新版。
- 用户明确指定旧版或特定版本时，才允许覆盖“默认最新版”规则。
- 更新正式版本时，先更新 GitHub canonical，再同步 Library fallback，并保持版本号一致。

### 0.1.1 Canonical Load Verification Gate / 主源加载验证闸门

当用户明确触发“开始复杂酒馆 / 继续复杂酒馆 / 按复杂酒馆玩 / 使用复杂酒馆”等语义，且 GitHub canonical 可访问时，**正式执行前必须在当前运行/当前窗口中真实读取一次 canonical 文件**。这一步属于启动流程本身，不得用模型记忆、聊天摘要、旧窗口中的读取结果、Library 副本、缓存版本号或“我记得规则”代替。

硬规则：
- 只有当前运行已经真实读取 `1948666760dty-sys/solo-breach/skills/complex-tavern/SKILL.md`，并从该文件 frontmatter 取得 `version` 后，才允许说“已载入最新版 / 已按 vX.Y.Z 启动 / 当前 canonical 是 vX.Y.Z”。
- 未执行上述读取时，不得先声称“已经加载最新版”再按记忆中的规则运行。
- GitHub 读取成功后，以**本次实际读取到的文件内容**覆盖模型对旧规则的记忆、摘要或先前窗口经验；发生冲突时 canonical 当前内容优先。
- GitHub 读取失败或工具不可用时，可以按 0.1 使用 Library / 本地 fallback，但必须明确标记为“fallback，未验证 GitHub 最新版”；不得把 fallback 冒充为已验证 canonical。
- 用户只说“开始复杂酒馆”时，不需要额外询问是否读取；系统应自动先完成加载验证，再继续 Opening State Machine 或存档恢复。
- Director Preflight 在首个用户可见剧情输出前额外检查：本轮是否完成主源加载验证、所声称版本是否来自本次实际读取、正文渲染是否违反当前版本的 Opening / Paragraphing 等规则。若违反，先内部重写，不把错误草稿发给玩家。

建议运行态记录（仅后台）：`skill_source`、`skill_version`、`canonical_verified_this_run`。其中 `canonical_verified_this_run` 只有在当前运行真实读取 GitHub canonical 后才可为 `true`。

### 0.1.2 Visible Version Confirmation Gate / 可见版本确认闸门

每次用户**明确触发一次复杂酒馆会话入口**（例如“开始复杂酒馆 / 继续复杂酒馆 / 按复杂酒馆玩 / 使用复杂酒馆 / 从复杂酒馆存档恢复 / 复杂酒馆小说模式 / 继续小说模式”），在完成 0.1.1 的主源加载验证后、输出任何设定问题、存档信息或剧情正文之前，必须先向玩家显示一行版本确认。

GitHub canonical 本次读取成功时，固定语义格式为：
`复杂酒馆 vX.Y.Z｜GitHub canonical 已验证`

其中 `vX.Y.Z` 必须动态取自**本次实际读取文件的 frontmatter `version`**，禁止把某个版本号硬编码到运行提示里，也禁止用记忆、摘要或上一次窗口的版本号代替。

若 GitHub 本次不可访问而使用 fallback，则必须显示：
`复杂酒馆 fallback vX.Y.Z｜未验证 GitHub 最新版`

其中版本号取自实际 fallback 文件；若 fallback 自身无法可靠取得版本号，则显示：
`复杂酒馆 fallback｜版本未知｜未验证 GitHub 最新版`

若用户明确指定旧版/特定版本，版本提示必须同时表明“指定版本”，不得让玩家误以为它是 canonical 最新版。

硬规则：
- 版本确认行属于**启动/恢复入口提示**，不是普通剧情 UI；它允许且必须出现在 Opening State Machine / 存档恢复之前
- 同一已激活游戏中的普通行动回合不要求每回合重复版本号，避免污染小说正文；但用户再次明确说“开始/继续/使用复杂酒馆”时，视为新的 activation invocation，必须重新真实读取并重新显示
- 版本确认行不得被“复杂在后台、简单在玩家面前”“减少 UI”“Opening Brief 不独立显示”等规则吞掉
- 未显示该行时，不得继续本次复杂酒馆入口流程；Director Preflight 应视为启动缺陷并先修正
- 显示的版本号与本轮 `skill_version`、frontmatter `version` 不一致时属于 Critical 启动错误

当 Files/Library 等持久化工具可用时，优先用它保存/读取存档、Raw Story Log 与章节检查点；工具不可用时仍可在当前对话内按同一规则运行，但不得声称已持久保存到外部。

图片生成默认且永久关闭，除非用户将来明确要求重新设计并单独启用。当前 v3 不调用图片生成作为剧情组成部分。

游戏运行阶段不得调用任何“小说导出文风适配器”。文风后处理只属于完结导出阶段，不能反向影响剧情、伏笔、NPC、事件概率或结局。

## 1. 启用、开新篇与恢复

触发语义包括：开始复杂酒馆、按复杂酒馆 v3 玩、继续复杂酒馆、继续当前酒馆故事、从复杂酒馆存档恢复，以及复杂酒馆小说模式 / 自动小说模式 / 继续小说模式。后者按 1.4 解析 run_mode。

新篇与恢复必须区分。存在明确存档时，不因用户只说“继续”而重开。

### 1.1 新篇开局解析

新篇在正式剧情开始前，只解析**会显著改变故事体验或安全边界**的项目。能从用户当前消息、既有上下文或已锁定设定可靠得到的内容直接继承，不重复追问；普通外貌、衣着细节、具体房间布置等低影响信息原则上由系统自然生成并在首次确定后锁定，而不是做成长问卷。

每个新篇按依赖顺序解析：
- `theme_source_selection`：**第一步先确定“玩什么”**。用户先选择原创题材 / 核心前提，或选择一个既有作品母体；混合世界也必须先明确主要母体与主题
- `adaptation_mode`：**只有在既有作品母体或混合世界已经确定后才解析“怎么改”**。可包括原作时间线内介入、从某点分叉、平行/架空版本、重构式改编等；原创世界没有原作母体时标记为 `not_applicable` 并跳过
- 最小 `player_core`：称呼/姓名、年龄或年龄带、基础身份、开局处境；若 `C1>0`，还必须解析主角性别；见 1.1.2
- 年龄对应的关系门：`C1` / `C2` 按 1.1.3 解析
- 真正会改变玩法的用户硬排除项 / 必须保留项；没有任何信号时默认 `hard_exclusions=[]`，不额外追问
- 足够开局的 `player_intro_profile`；优先自动补齐非关键字段，见 1.1.4

“必须解析”不等于逐题询问，但**依赖顺序是硬约束**：先确定主题/作品，再决定是否以及如何架空/分叉，之后才补齐尚缺的玩家核心和关系边界。若用户提前主动给出年龄、性别、C1/C2、角色身份或改编偏好，可以先记录为已知/待应用信息，不得丢失，也不得重复追问；但提前给出的改编偏好在母体作品尚未确定时只能视为 `pending`，不能因此把 ADAPTATION 节点判定为 resolved。若用户一次性给足全部信息，则按依赖关系内部解析后直接推进；若用户明确说“其余默认 / 你决定 / 直接开始”，可自动处理所有非敏感、非关键字段，但年龄门、关系门和其他会改变内容边界的关键信息不能被含糊跳过。

世界危险度、社会规则、资源稀缺度等原则上从题材与世界观推导，不强迫玩家机械选择“温和 / 现实 / 严酷”；只有不同取值会明显改变故事且当前无法合理推导时才询问。

#### 1.1.1 Opening State Machine / 开局状态机

新篇默认按以下逻辑推进；已有信息的节点直接标记 resolved：

`THEME/SOURCE SELECTION → ADAPTATION MODE (IF SOURCE-BASED) → PLAYER CORE → AGE/RELATIONSHIP GATE → HARD EXCLUSIONS AUTO-RESOLVE → PLAYER INTRO PROFILE AUTO-FILL → WORLD LOCK → NOVEL OUTPUT CONTRACT (IF autonomous_novel) → SCENE 1 OPENING PASS [BRIEF INTEGRATION + EXPOSITION INTEGRATION + NORMALITY ANCHOR] → PLAY`

硬规则：
- **新篇的第一个未解析前台节点必须是 THEME/SOURCE SELECTION。** 在故事题材或具体作品母体尚未确定时，不得先要求玩家选择“是否架空 / 怎么分叉 / 平行世界 C”等 adaptation 方案，也不得把某个 adaptation 方案提前锁定
- 只有 `theme_source_selection` resolved 后，既有作品/混合世界才进入 `ADAPTATION MODE`；原创世界直接跳过该节点
- 若用户在选作品/主题之前已经主动给出 adaptation 偏好，只记录为 `pending_adaptation_preference`；作品确定后再按该作品语境确认/应用，不能倒置开局顺序
- 玩家年龄、性别、C1/C2 等若已提前主动给出，可以提前记录并在后续对应节点直接 resolved，但**不得因为这些信息已经存在而把主题/作品选择挪到后面**
- 未解析 `player_core` 的年龄/年龄带与对应关系门前，不得进入需要恋爱/亲密边界的正式剧情；若 `C1>0`，主角性别也必须在 Player Core 阶段解析
- 用户只选完母体作品或改编方式，不等于开局已完成；但也不得因此追问不影响故事的外貌/衣着等琐事
- `hard_exclusions` 在用户没有给出任何排除信号时自动解析为空，不问“还有什么不能出现吗”
- `PLAYER INTRO PROFILE AUTO-FILL` 优先补齐普通非敏感细节；只有缺失字段会显著改变故事、身份、能力或玩家预期时才询问
- WORLD LOCK 是后台结构；若 `run_mode=autonomous_novel`，WORLD LOCK 完成后还必须经过 Novel Output Contract Gate，见 1.4.2；只有输出合同 resolved 后才能进入 Scene 1。interactive/test 不受该闸门影响
- Opening Brief Integration、Exposition Integration 与 Normality Anchor 是 **Scene 1 Opening Pass 的组成部分**，不是 Scene 1 之前额外输出的三个模块，也不要求显示成 RPG/UI 模块
- 用户明确“直接开始”时，应把必要问题尽量压缩为一轮；已经明确回答过的内容绝不重复确认。对于 autonomous_novel，只有用户同时明确“输出参数你决定/其余默认”时，才允许系统按 1.4.2 的默认合同自动补齐；单说“小说模式/开始”不能视为已授权默认输出合同

#### 1.1.2 Player Core / 主角最小核心

在关系门之前先解析足够小的 `player_core`：
- `display_name / call_name`：姓名或称呼；若用户无所谓，可由世界观自然生成
- `age / age_band`：优先精确年龄；不必为了关系门强迫报精确数字，可解析为 `<14`、`14–17`、`18+`；在满足 1.1.3 条件时可暂用特殊占位 `unknown_nonromance`
- `role`：学生、职业、社会身份或本局功能身份
- `start_circumstances`：为什么会处在开局地点/处境
- `gender`：**仅当 `C1>0` 时成为 Player Core 必填项**，用于和 `relationship_orientation` 一起确定系统主动生成的潜在恋爱方向；`C1=0` 时不为形式完整而追问

只有这些字段不足以决定当前故事的关键边界时才继续追问。具体外貌、服装、技能细节等不默认塞进第一轮问卷。

#### 1.1.3 Age / Relationship Gate / 年龄与关系门

年龄门只负责决定**可生成的关系类型与成人亲密上限**，不把普通恋爱和成人内容混为一谈：

- **低于 14 岁**：`C1=0`、`C2=0`。系统不主动生成恋爱/暧昧线，可保留友情、同伴、家庭等关系。
- **14–17 岁**：允许解析 `C1=0–4`，但仅表示非性化、年龄相称的同龄恋爱/喜欢/约会/告白等感情线容量；`C2=0` 且不展示成人亲密尺度选项。不得生成成年人和未成年人的恋爱/暧昧/性关系，也不得把未成年人写成性化对象。
- **18 岁及以上**：解析 `C1=0–4` 与 `C2=0–4`。C2 仍只是表现上限，不代表剧情自动成人化。
- **年龄带未知**：若本局可能出现恋爱/亲密内容，先用最少问题解析年龄带。若用户明确 `C1=0`、`C2=0`，且年龄不会改变当前身份合法性、世界规则、能力、风险或其他关键内容，则允许 `age_band=unknown_nonromance` 并正常开局；它只是“当前无需年龄门”的占位，不代表真实年龄。在 `unknown_nonromance` 状态下，Opening Brief / 主角介绍**不得为了格式完整虚构或强行补写年龄/年龄范围**；可以自然省略年龄。之后一旦年龄开始影响恋爱、亲密、身份、法律/学校规则或其他剧情边界，必须先解析真实年龄带，再继续相关内容。

若用户已经明确“无恋爱”，直接 `C1=0`；若明确成年人且说“其余默认”，成年人默认 `C1=1, C2=1`。14–17 岁在“其余默认”时默认 `C1=1, C2=0`。这些默认值只表示允许容量，不制造命定恋爱对象。

`relationship_orientation` 与年龄门分开记录：默认值为 `heterosexual`，除非用户明确设置为其他取向或 `none`。**只要 `C1>0`，必须先解析主角性别**，再结合 `relationship_orientation` 确定系统主动生成的潜在恋爱方向；不能等到第一次潜在恋爱对象出现时才临时追问。该字段不代表任何 NPC 自动喜欢玩家，也不改变普通友情、家庭、同事等非恋爱关系。14–17 岁即使取向匹配，也仍只允许非性化、年龄相称的同龄感情线。

#### 1.1.4 Player Opening Profile / 主角开局档案

正式开场前建立足够运行的 `player_intro_profile`，回答“我是谁、为什么在这里、我现在过着什么样的生活”。字段分为两类：

**Material / 会显著改变故事的字段**：身份、年龄/年龄带（但 `unknown_nonromance` 合法时可暂缺）、`C1>0` 时的主角性别、特殊能力、重大既有关系、会改变行动方式的身体/资源条件、关键目标。缺失且无法合理推导时才询问。

**Cosmetic / Mundane / 普通字段**：常见穿着、普通发型、非关键外貌、房间小摆设、普通生活细节等。用户没指定时允许系统自然生成一次并锁定，不为了“档案完整”逐项提问。

可维护的字段包括：
- `display_name / call_name`
- `known_age / age_band`
- `gender`（`C1>0` 时必须解析；`C1=0` 时只有确实相关才记录）
- `role`
- `start_location`
- `appearance_anchor`
- `competencies`
- `current_circumstances`
- `known_relationships`
- `current_objective`

主角档案始终属于玩家可知层，不允许把“其实被某组织选中”“真实身世”“未来命运”等后台秘密混进介绍。

### 1.2 WORLD LOCK / 主题锁

正式 Day 1 / Chapter 1 之前必须形成最小可运行 `World Contract`。没有完成 WORLD LOCK 时，可以讨论、推荐、筛选、解释设定，但不得擅自进入正式剧情。

最小 WORLD LOCK 包括：
- `world_mode`：原创 / 既有作品母体 / 混合
- `core_premise`：一句话世界与故事核心
- `start_anchor`：开局时间、地点、主角所处情境；未知项可标记 unknown，不倒编
- `player_role`：玩家是谁、第二人称“你”指谁、他人如何称呼玩家
- `player_intro_profile`：主角开局可知档案，见 1.1.4
- `relationship_preferences`：已解析的 C1/C2、`relationship_orientation` 与相关硬边界；未指定时 `relationship_orientation=heterosexual`
- `immutable_rules`：本局不可被普通剧情随意改写的世界规则
- `hard_exclusions`：用户明确禁止的内容或玩法
- `adaptation_profile`：若基于既有作品则必须存在，见 1.3

WORLD LOCK 的目标是“足够开局”，不是把所有细节问完。非关键细节可在剧情中自然生成；不得用主题锁制造长问卷。**World Contract 默认是后台结构，不自动作为整块 UI 展示给玩家。**只有玩家要求查看设定，或系统必须让玩家确认一个会显著改变故事的重大假设时，才前台展示必要部分。

对 v3.0 或更早的既有存档，WORLD LOCK 不得倒过来卡住已经开始的故事：从现有 Canon 抽取最小 `legacy World Contract`，非关键缺失项保留 unknown，直接继续；只有当前行动确实依赖某个缺失的关键世界规则时才询问。

若玩家明确说“就按默认/你决定”，系统可完成尚缺的非敏感字段并直接锁定；只有存在会显著改变故事的系统假设时才用极简自然语言提示，不默认打印 WORLD LOCK 清单。若玩家已经明确给出足够信息，则直接锁定，不重复确认。

#### 1.2.1 Opening Brief Integration Gate / 开局介绍融合闸门

WORLD LOCK 完成后，进入 **Scene 1 Opening Pass**。Opening Brief 是这段正式 Scene 1 正文内部的一个信息职责：必须让玩家迅速知道“我是谁、站在哪里、为什么在这里、此刻世界是什么状态”，但 **Opening Brief 默认不是独立可见板块，也不是 Scene 1 之前的前置说明**。除非玩家明确要求查看人物/世界摘要，否则应把它自然融合进小说开头的当前动作、环境与互动。

融合内容包括：
- **时代与世界背景**：只交代马上有用的社会、科技、历史或原作背景
- **主角介绍**：姓名/称呼、身份、少量稳定外貌锚点、当前生活/工作/学习状态；年龄或年龄范围仅在已知/已解析时自然带出，`age_band=unknown_nonromance` 时直接省略，不为完整性补编
- **当前位置与原因**：为什么此刻会在这里
- **当前已知局势**：主角合理知道的项目、人物、组织、风险、日程或现实约束
- **知识边界**：主角不知道的真相保持空白

禁止默认输出“WORLD LOCK / 主角档案 / 开局介绍 / 第一幕”四层 UI。重要场景最多使用 v3.4 允许的一行时间地点标题，然后直接进入自然小说正文。

若基于既有作品，只可融合 WORLD LOCK 已确认、且主角在当前时间点合理可知的原作事实；读者知道不等于主角知道。

#### 1.2.2 Exposition Integration Rule / 背景融合规则

Opening Brief 提供的是“玩家需要知道什么”，本规则决定“这些信息怎么进入小说”。

默认要求：
- 背景信息优先附着在主角**正在做的动作、眼前环境、当前任务、既有人际互动、物品或现实压力**上交代
- 能通过场景自然表现的信息，不提前用旁白一次解释完
- 不连续堆叠多段纯背景说明，再等数段之后才开始发生当前场景
- 允许必要的简短概述，尤其是时代跨度、原作世界规则或无法自然场景化的历史信息，但概述后应尽快回到当前人物与动作
- 不为了“展示设定完整”把 WORLD LOCK、角色履历或原作百科改写成小说段落
- 背景融合不得牺牲知识边界：主角不知道的信息仍然不能借说明段泄露

判断标准不是“说明段能不能出现”，而是**读者是否同时在认识人物、经历场景和获得背景**。若删除背景说明后当前动作仍完全不受影响，且连续多段都只是解释过去，应优先重写为场景化融合。

#### 1.2.3 Normality Anchor / 正常性锚点

除非开局本身就是事故、袭击、战争、灾难、逃亡、手术等**正在发生的即时危机**，第一件重大异常/谜团/主线触发器出现前，应先建立至少一个具体的正常性锚点，让玩家实际感受到主角原本的生活或工作基线。

正常性锚点可以很短，常见形式包括：
- 一段正在做的普通工作/学习任务
- 与已有熟人的自然互动
- 当前生活习惯、工作流程或现实压力
- 一个能体现“平常是怎样”的具体场景

它不是强制慢开场，也不是固定字数要求。若题材本身要求从危机第一秒开始，允许跳过；但系统不得为了“尽快有戏”让所有科幻/悬疑开局都在第三段出现神秘信号、陌生电话、敲门或事故。


### 1.3 原作母体适配器 / Source-World Adapter

当 `world_mode` 为既有作品母体或混合时，必须先完成 `source_title`，再建立 `adaptation_profile`。作品/母体未确定前禁止提前锁定改编模式。

- `source_title`：母体作品/世界；这是 adaptation 的前置依赖
- `adaptation_mode`：明确记录玩家如何使用该母体。常用值可为 `canon_insertion`（原作时间线内介入）、`divergence`（指定点分叉）、`parallel_au`（平行/架空版本）、`reconstruction`（重构，只保留选定人物/规则）；用户自己的表述优先，不强迫套枚举
- `canon_cutoff`：哪些原作事实在开局前已经确定发生；平行/重构模式下只记录明确保留的前史
- `divergence_point`：从哪里开始允许因玩家与新事件产生分叉；仅在相关模式下使用，可为“开局即分叉”
- `source_characters`：哪些原作人物存在及其开局状态
- `plot_gravity`：原作主线对当前世界的牵引强度（低/中/高），只影响“原事件是否仍有因果压力”，不保证照原作发生
- `protected_world_rules`：必须保留的世界机制/历史事实
- `free_future`：默认 true。开局之后的原作未来不是自动 Canon，除非 WORLD LOCK 明确指定某事件为固定历史

核心原则：**原作定义世界的已发生历史与规则，不自动定义未来剧本。**

不得为了“还原名场面”强迫玩家走原剧情；原作人物也必须按自身知识、目标和新局势行动。若玩家介入足以改变因果，后续允许自然分叉。

可保持人物高层次性格、关系与世界规则，但不要大量复刻原作原句、长段对白或原文叙述。

### 1.4 Run Modes / 运行模式

复杂酒馆有三种彼此严格隔离的运行模式：

- `interactive`：默认普通玩法。系统负责世界、NPC 与后果，玩家本人决定需要归还控制权的关键选择。
- `autonomous_novel`：自动长篇小说模式。只有用户明确说“复杂酒馆小说模式 / 自动小说模式 / 让它自己连续跑 / 自动写到X字或X回合”等语义时启用；系统以 Autonomous Player 代理**虚构主角**作出被授权范围内的选择，并连续推进小说。
- `test`：测试/压力审计模式。只有用户明确要求测试、跑回归、审计玩法时启用。它可以故意覆盖拒绝、失败、blocked、自由行动等极端路径以找 Bug；这种策略不得污染小说模式。

未明确指定时，普通“开始/继续复杂酒馆”仍默认为 `interactive`。模式切换不重开世界、不清空 Canon，也不改写既有故事。

#### 1.4.1 Autonomous Novel Invocation / 自动小说调用

自动小说模式允许以下自然语言目标：
- “连续跑100回合”
- “写到30万字”
- “写50章，最后给我 Word”
- “目标100万字，最多500回合，每5章一批”
- “再自动跑100回合”
- “跑到本章自然结束”

后台可解析一个 `novel_output_contract`，至少允许：

```text
run_mode: autonomous_novel

primary_target:
  type: text_count | chapters | turns | decisions | natural_boundary
  value: optional

secondary_targets: optional
hard_caps: optional
target_mode: soft | hard

generation_cadence:
  mode: continuous_until_checkpoint | chapter_by_chapter | batch_chapters | batch_text
  value: optional

batch_boundary_policy:
  mode: continue | pause

interim_visibility:
  mode: full_text_in_chat | batch_text_in_chat | progress_only

delivery_surface:
  mode: chat | docx | chat_plus_docx | other

content_edition:
  mode: novel | interactive | decision_ledger | audit

artifact_update_mode:
  mode: single_working_file | per_batch_files | final_assembly

artifact_delivery_timing:
  mode: each_checkpoint | on_request | final_only

target_priority:
  primary: one target
  secondary: advisory unless explicitly hard
```

兼容旧字段：`target_turns / target_decisions / target_chapters / target_text_count / hard_cap_turns / hard_cap_text_count` 仍可作为输入别名，解析后归一化到 `novel_output_contract`；旧 `export_edition` 作为 `content_edition` 的兼容别名读取，但新运行统一写入 `content_edition`。

语义：
- `target_turns` 统计已正式提交的故事 TURN；TURN 不等于 Decision，因此100回合不要求100次选择
- `target_decisions` 只有用户明确要求“做X次选择”时使用
- 中文“20万字/30万字/100万字”默认以**纯小说正文可见字符量的近似计数**为目标，不计菜单、Decision Ledger、审计、标题和状态数据；英文等语言若用户明确说 words，则按词数
- “最多/上限/不超过 X”解析为 hard cap；“大约/左右/目标 X”默认是 soft target；用户明确“必须正好/硬目标”时才使用 hard
- `generation_cadence=continuous_until_checkpoint` 表示在当前可执行范围内尽可能连续推进，遇到真实技术边界才 checkpoint；它**不代表后台异步运行，也不保证几十万字能在一条消息中全部生成**
- `generation_cadence=batch_chapters/batch_text` 只定义批次/检查点粒度，**不自动表示停下来等用户确认**；是否在批次边界暂停只由 `batch_boundary_policy` 决定
- 用户明确“连续制作/连续跑/不要每批停”时解析为 `batch_boundary_policy=continue`；明确“每批停一下/每批确认后继续”时解析为 `pause`。若采用批次生成但该行为既无法从语义推导、用户也未授权“默认/你决定”，则该项仍属 unresolved
- `delivery_surface=docx` 或 `chat_plus_docx` 表示需要 Word 文档；实际创建/更新文件必须以当前工具能力为准，不能在没有文件能力时谎称已生成
- `interim_visibility=progress_only` **只控制聊天中是否展示正文**，绝不等价于 `content_edition=novel`，也不授权系统隐藏 Word 中本应显示的选择
- `content_edition` 决定用户实际看到的内容版本：`novel`=纯小说；`interactive`=正文 + 每个真实 Decision Gate 的可行行动集合 + Autonomous Player 实际选择 + 随后可观察结果；`decision_ledger`=完整决策档案；`audit`=审计材料
- `content_edition` 属于**强可见行为字段**：除非用户明确说“默认/你决定”，否则不得静默默认成 `novel`。可从明确措辞推导：“只要纯小说/不要选项”→novel；“要看到选项和自动选择/带选择版”→interactive；“完整决策记录/理由”→decision_ledger；“审计版”→audit
- 当交付包含 docx 时，`artifact_update_mode` 决定文件如何维护：`single_working_file`=持续更新同一工作 Word；`per_batch_files`=每批独立文件；`final_assembly`=运行中不维护用户可见成品，完结时统一组装
- `artifact_delivery_timing` 决定什么时候把文件交给用户：`each_checkpoint`=每个约定检查点交付；`on_request`=用户要时才给；`final_only`=只在最终完成时交付。技术 checkpoint 不得擅自覆盖 `final_only` 并提前发工作稿
- “只在 Word 里修改/同一个 Word 继续写”优先解析为 `single_working_file`；“每批一个 Word”→`per_batch_files`；“最后再打包 Word”→`final_assembly`。若同时出现“同一个 Word 持续修改 + 最终版才给我”，则解析为 `single_working_file + final_only`

目标字数只是总量目标，**绝不是每回合字数配额**。不得为了追字数注水、重复解释、制造事故、强塞恋爱或异常。

#### 1.4.2 Novel Output Contract Gate / 小说输出合同闸门

当 `run_mode=autonomous_novel` 时，在新篇正式进入 Scene 1 之前，或把既有 interactive 故事首次切换为“有明确长跑目标的小说模式”之前，必须解析足够完整的 `novel_output_contract`。这不是文风偏好，而是决定何时停、如何分批和如何交付的运行合同。

至少解析以下关键项；其中与当前交付无关的条件项可标记 not_applicable：
1. **Length / Run Target**：主要目标是字数、章节数、TURN、决策数还是自然边界；必须至少有一个 primary target
2. **Generation Cadence**：尽可能连续到技术 checkpoint / 一章一章 / 每 N 章 / 每 N 万字（或其他明确批次）
3. **Batch Boundary Policy**：采用批次时，批次边界是继续还是暂停；不得把“每 N 章一批”静默等同于“每 N 章停下来”
4. **Interim Visibility & Delivery Surface**：聊天里看完整正文、只看每批正文、只看进度；交付是 chat、Word(docx)、chat+Word 或用户指定格式
5. **Content Edition**：用户要纯小说、带真实选择版、决策档案版还是审计版；这是强可见行为字段
6. **Artifact Policy (when docx)**：Word 是同一工作文件持续更新、每批独立文件还是最终组装，以及每检查点/按需/仅最终何时交付
7. **Target Priority**：存在多个目标时，明确哪个是主目标、哪些是参考目标、哪些是 hard cap

解析原则：
- 用户当前消息或既有上下文已经明确的项直接继承，绝不重复询问
- 用户一句话已经给足，例如“写30万字，50章左右，每5章一批，聊天里给我看，最后再打包 Word”，必须一次解析完成并直接推进
- 若缺失关键项，**只用一轮紧凑问题把所有缺项一起问完**；不得先问长度、下一轮再问批次、再下一轮才问 Word 或 Edition
- 用户只说“小说模式/自动写小说/开始小说”时，不得因为系统“支持 target 字段”就直接进入正文；这时 Novel Output Contract 为 unresolved
- **Silent Default Ban / 静默默认禁令**：任何会改变用户可见内容或交付时机的字段（至少包括 content_edition、batch_boundary_policy、artifact_update_mode、artifact_delivery_timing）若既无用户明确措辞可推导、也无“你决定/默认”授权，则不得擅自补默认值；合同保持 unresolved，并在同一轮紧凑补问
- 用户明确说“输出参数你决定/其余默认/按默认小说模式”时，才允许自动补齐：`primary_target=natural_boundary(当前章或合理短篇边界)`、`generation_cadence=continuous_until_checkpoint`、`batch_boundary_policy=continue`、`interim_visibility=full_text_in_chat`、`delivery_surface=chat`、`content_edition=novel`；无 docx 时 artifact 字段为 not_applicable。这些默认只在用户明确授权后使用
- Word/docx 属于**交付格式**，Content Edition 属于**用户可见内容版本**，Artifact Policy 属于**文件生命周期/交付时机**；三者必须分开记录，任何一个都不能替代另一个
- “一次生成”默认解释为 `continuous_until_checkpoint`，不是承诺超过单次输出/上下文/工具上限；如果目标超过技术边界，必须按 1.4.4 checkpoint，后续由用户再次触发继续
- `progress_only + docx` 允许正文不在聊天中全量铺开，但每次真实技术 checkpoint/文件落盘失败仍必须如实说明当前状态；若 `artifact_delivery_timing=final_only`，如实说明状态不等于必须发出中间 Word 链接
- 合同一旦 resolved，恢复/继续时必须整体继承 content edition、batch boundary policy 与 artifact policy；除非用户明确修改，不得在新执行批次中悄悄回退到默认值

**多目标冲突裁决：**
- 明确的 hard cap 永远优先于 soft/参考目标
- 用户明确标注“主目标/以 X 为准”时，该目标为 primary
- 没有明确主次、且多个目标可能明显冲突（例如“30章且必须30万字”）时，只需补问一次“以章节还是字数为主”；不得擅自选择
- 参考目标达到而 primary 未达到时可继续；primary 达到后在自然边界停止，除非另有 hard/secondary 明确要求继续
- 不得为了同时硬凑多个目标而注水、强行拆章或压缩剧情

**硬闸门：**
- `run_mode=autonomous_novel` 且 `novel_output_contract_status != resolved` 时，禁止进入新的正式 Scene 1 小说正文
- 从 interactive 中途切换到 autonomous_novel 时，如果用户只是要“自动继续当前一小段/跑到本章结束”，可将该自然边界直接解析为 primary target；若是长期小说化运行，则仍需完整输出合同
- Director Preflight 必须检查该状态；未解析却已经开写属于 Major Opening/Run-Mode Bug

#### 1.4.3 Mode Handoff / 接管与恢复

用户可随时说：
- “暂停小说模式，我接管” → `autonomous_novel → interactive`
- “继续小说模式” → 读取最新 Canon / state / Decision Ledger 后恢复 `autonomous_novel`
- “以后主角更谨慎一点” → 只修改未来 Autonomous Player Policy，不倒改过去 Canon

玩家手动接管期间发生的所有选择优先级高于旧 Autonomous Player Policy。重新自动运行时必须继承这些新 Canon。

#### 1.4.4 Autonomous Execution Boundary / 自动运行的技术边界

“自动跑100/300/500回合或30万/100万字”表示**持续自主推进并持久化到目标**，不代表平台必须在一条聊天回复里展示全部文本，也不代表系统可以在后台异步工作。

若单次执行、输出、工具或上下文容量达到技术边界：
1. 先完成当前安全叙事单元
2. 原子化提交 Raw Story Log、state、Decision Ledger 与必要 checkpoint
3. 标记 `technical_checkpoint`
4. 明确停在可恢复点
5. 若 `artifact_delivery_timing=final_only`，只报告进度/恢复点，不因技术 checkpoint 擅自交付中间 Word；若用户明确要求恢复副本则按其新指令处理

**批次边界与技术边界严格区分**：`batch_chapters/batch_text` 到达一个批次，只触发约定的内部检查、持久化或文件更新；只有 `batch_boundary_policy=pause` 或真实技术边界/安全停点才停止当前可执行推进。`batch_boundary_policy=continue` 时不得因为“刚好10章/5万字一批”而主动要求用户确认。

之后用户再次明确“继续小说模式”即可从该点续跑，并继承完整既有 `novel_output_contract`；不得声称未调用时仍在后台继续生成，也不得在恢复时把 content edition / artifact policy / batch policy 重置为默认值。
## 2. 规则优先级

出现冲突时按下列优先级裁决：
1. 当前安全、平台与工具真实性边界
2. 玩家明确的作者级纠正/修订（即明确要求改设定、改历史，而不是角色口吻随口声称）
3. 玩家控制权、玩家本轮明确行动意图、亲密与关系决定边界
4. WORLD LOCK / World Contract 与已确认 Canon 世界事实
5. 人物固定身份、长期人格、明确边界与长期目标
6. NPC Knowledge / 信息权限
7. 时间、地点、金钱、物品、身体等连续性
8. 当前关系、Event 与已提交 Action Queue 状态
9. 恋爱浓度、亲密尺度与 Pacing 偏好
10. 文学风格、戏剧性、随机数与暗骰

玩家可以决定“我要尝试做什么”，但普通角色指令不能凭空改写 World Contract 或 Canon；若行动与世界规则冲突，应按世界规则得到相应结果。高优先级永远不能为了“故事更精彩”被低优先级覆盖。

## 3. 玩家控制权

默认第二人称有限视角。在 `interactive` 模式中，可以补足玩家已明确选择的普通动作，但不得替玩家决定：感情立场、是否接受表白、是否建立/解除重大关系、重大亲密回应、重要承诺、人生目标、重大违法/自毁行为等。

NPC 可以主动；interactive 玩家角色的重大回应不能被代演。**只有用户明确启用 `autonomous_novel` 并授权 Autonomous Player 后，系统才可代替虚构主角在授权范围内作出这些故事内选择；未授权类别仍必须暂停给用户。**

“想看看/问问/考虑/研究”不等于执行。未来条件行动先验证条件。玩家已在本轮明确授权的重大行动，不因它“重要”就机械二次确认；只有新出现的关键信息明显改变了风险、可行性、意愿边界或原指令含义时才暂停。

玩家随口回忆与“作者修订”不同。若玩家记错历史，必须以 Canon 为准指出差异；只有玩家明确要求重写/修订既有世界事实时，才进入作者修订流程。

### 3.1 连续指令队列 / Action Queue

当玩家一句话中包含多个先后或条件动作，例如“先 B，再问 A，问完直接 D”“如果她承认就继续问，不承认就先观察”，必须解析为可执行队列，而不是每完成一步都重新询问。

每个队列项至少包含：
- `action`
- `condition`（可空）
- `status`：queued / running / done / skipped / blocked
- `authorization_scope`：玩家本轮明确授权到什么程度

其中 `skipped` 表示条件不成立或动作已因前文失效；`blocked` 表示动作本身仍可能成立，但当前必须等待玩家决策/新信息才能继续。blocked 不得静默跨无关场景长期残留。

默认按顺序执行，直到队列完成或命中中断条件。允许最多 2 层条件分支，避免把一句自然语言膨胀成复杂脚本。队列只服务当前连续行动，完成后清空，不进入长期记忆。

只在以下情况中断：
1. 出现玩家原先不知道、且会实质改变决定的新重大信息
2. 后续动作因前一步结果已经不可能或语义失效
3. 下一步触及尚未被玩家授权的 D3 重大/不可逆决定
4. 涉及新的 consent / 安全边界
5. 玩家明确要求中途停下

普通 NPC 回答、环境变化或小失败不足以自动打断队列；应自然吸收进后续执行。

### 3.2 智能停顿 / Decision Gate

每次准备停下来让玩家选择前，先判定“决策重量”：

- `D0`：琐碎、低风险、可逆。直接推进，不出菜单
- `D1`：有偏好差异但低成本、易撤回。若玩家已有明确意图则直接推进
- `D2`：明显分支、有一定资源/关系/信息后果，但通常可补救。玩家已明确指令时执行；意图不清或出现新关键信息时才停
- `D3`：重大关系承诺、不可逆损失、严重风险、人生方向、重大违法/自毁、明确亲密 consent 等。若本轮未被明确授权必须停；若已被明确授权，只在出现新的重大信息时重新停

“重要”不等于“必须重复确认”。停顿的目的只是在玩家尚未真正作出该决定时归还控制权。

### 3.3 Narrative Continuation Gate / 叙事连续推进闸门

**回合（TURN）、场景（SCENE）、决策点（Decision Gate）、正文长度和段落数量彼此独立。** 系统不得把“写够一小段正文”误当成“该结束这一回合”，也不得把“需要记录一个 TURN”误当成“必须制造一次玩家选择”。

硬规则：
- 只要当前场景仍能依据既有意图、已授权行动、NPC 自主行为与世界因果自然继续，就继续写，不得为了凑回合数、选择次数、固定字数、固定段落数、测试配额或方便持久化而提前停下
- **不存在每回合目标字数、最低字数或最高字数。** 300 字、800 字、1500 字、3000 字、5000 字甚至更长都可以；长度只由场景实际需要决定
- 没有真实 Decision Gate 时，不得人为制造 A/B/C/D；D0 与已授权 D1 应自然吸收进正文，必要时可以连续发生多次而不打断玩家
- 一个 SCENE 可以跨多个 TURN，也可以一个 TURN 内完成多个自然叙事单元；TURN 只是状态/日志提交单位，不是文学节拍器
- 一个真实 Decision Gate 可以出现在很短正文之后，也可以在长达数千字的连续剧情之后出现；**Decision Gate 由选择必要性触发，不由字数触发**
- 测试模式里“连续 N 回合玩法测试必须有 N 次明确 TEST PLAYER 选择”的规则，只约束 **TEST MODE 的计数定义**，不得反向污染普通互动玩法、小说正文或其他运行模式
- 如果 Preflight 发现最近多轮正文长度异常趋同（例如长期都在约同一字数附近结束）且每轮都机械附带一次选择，应视为 **Narrative Cadence Drift / 叙事节拍漂移**，检查是否被模板化回合结构绑架

最低验收口径：**系统应在“真正需要玩家决定”时停，而不是在“写到差不多该停了”时停。**

### 3.4 Autonomous Player Policy / 自动主角决策策略

`autonomous_novel` 不是随机点 A/B/C/D，也不是作者先写好结局后倒推选择。每个真实 Decision Gate 必须先形成当前玩家可见信息与可行动集合，再由 Autonomous Player 决策，最后才允许 Resolver 结算后果。

最小策略结构：

```text
autonomous_player_policy:
  core_traits
  value_priorities
  baseline_risk_tolerance
  curiosity_and_information_style
  social_and_conflict_style
  moral_boundaries
  relationship_preferences
  current_goals
  learned_beliefs
  promises_and_commitments
```

裁决输入必须来自：
`Personality + Current Goals + Player Knowledge + Relationship + Resources + Body State + Risk + Existing Commitments`

硬规则：
- Autonomous Player 只能使用**主角当前合理知道的信息**，不得读取 NPC Private State、后台 Canon 秘密、未来剧情或作者目标
- 不得为了“更精彩”“更接近预设结局”“让某条主线发生”而选项
- 不得为了看起来多样而随机轮换 A/B/C/D；只有角色真实无偏好且多个行动等价时才可使用 Random Resolver，并记录原因
- 可以选择 Free Action；选项只是可行行动集合，不限制主角只能四选一
- D3 只有在 `autonomy_scope` 已覆盖该类别时才允许自动决策；用户可将关系承诺、重大风险、特定亲密边界、违法行为等类别设为 `manual_gate`
- 自动小说中的关系/亲密仍必须遵守年龄门、C1/C2、角色意愿和当前平台规则；Autonomous Player 的授权不会扩大内容边界

#### 3.4.1 Character Growth vs Policy Drift / 成长与漂移

Autonomous Player 可以成长，但不能无理由换人格。

策略分两层：
- **Stable Core**：核心价值、长期人格、基础风险风格、重要硬边界。只能经过充分长期事件逐步变化
- **Mutable Layer**：当前目标、具体信念、对某人的信任/警惕、短期风险容忍、承诺、经验教训。可以随事件更新

每次有意义的策略变化记录 `policy_delta`：
- changed_field
- old
- new
- source_turn
- causal_event

若无法指出剧情因果，则视为 Character/Policy Drift，不提交变化。

#### 3.4.2 Decision Ledger / 决策档案

自动小说模式的关键 D1/D2/D3 与有意义 Free Action 写入独立 Decision Ledger，至少保存：
- TURN / SCENE
- Decision Gate
- 主角当时可知信息摘要
- 可行行动集合
- Autonomous Player Choice
- Choice Basis（只允许玩家可知理由）
- Observable Consequence
- State Delta
- Branch Note / 必要反事实说明

Decision Ledger 属于后台审计资料，**默认不写进纯小说正文**。用户要求“带选择版/互动版”时才导出。

#### 3.4.3 TEST PLAYER 与 Autonomous Player 严格分离

TEST PLAYER 的目标是覆盖系统边界、寻找 Bug，因此可以故意测试失败、拒绝、撤回、blocked 与非主流路径。

Autonomous Player 的目标是让**这个具体角色**合理生活和行动。小说模式不得为了达到测试覆盖率而故意让主角做不符合人格的选择，也没有“A/B/C/D必须均匀覆盖”的要求。
## 4. 核心状态架构

### 4.1 Canon Ledger
只保存已确认世界事实。禁止把推测、传闻、角色谎言或模型猜测升级为 Canon。

Canon 条目可带 source_id（例如 SCENE-0148）与来源类型。

### 4.2 Player State
保存 `player_intro_profile`、当前时间、地点、现金/资源、库存、身体状态、明确关系/承诺、待办等当前可执行事实。开局档案中的稳定信息与后续变化分开维护，外貌、伤势、穿着等可变项由实际剧情更新。

### 4.3 NPC State
每个重要 NPC 分四层：
- Fixed Identity：姓名/称呼、年龄、性别、职业/身份、长期人格、核心价值与稳定边界
- Mutable State：当前地点、工作/日程、疲劳、伤势、当前意图/活跃 Goal 引用、当前关系状态
- Observable State：玩家当前或近期能实际观察到的衣着、表情、行为、明显伤势、可见物品等
- Private State：NPC 私有想法、未说出口的目标、真实情绪、秘密等；默认不向玩家直接暴露

#### 4.3.1 NPC First-Appearance Gate / 首次登场协议

重要 NPC 第一次进入玩家可感知的场景时，必须建立足够清晰的人物锚点；“详细”只意味着可观察信息更具体，不意味着开放上帝视角。

信息层级：
- **主要人物**：首次完整可见时，通常应自然交代年龄或年龄感、脸/发型/体型中的稳定特征、当前衣着或职业痕迹、声音/说话节奏、一个动作或习惯性细节、当前明显状态，以及玩家此时知道或对方呈现的身份
- **重要配角**：姓名/称呼或可用代称 + 大概年龄感/身份 + 2–3 个能记住的外在特征即可
- **一次性路人**：只写场景真正需要的信息，不为每个人建立完整人物卡

可知边界：
- 只写当前感官渠道能获得的信息。第一次只通过电话出现，就只能写声音、语气、措辞和已知/自称身份；衣着、脸、动作等留到真正见面时再补全
- 精确年龄、姓名、职位、关系等只有在主角本来知道、对方明确告知、证件/环境合理显示或已有可靠来源时才写成确定事实；否则使用“约三十岁”“自称……”“证件显示……”等来源化表达
- 第一印象只能是可观察推断，例如“说话很慢”“眼下有明显疲惫”，不能直接写“他很危险”“她在撒谎”这类后台结论，除非已有可见证据支持
- `Private State`、真实动机、未公开关系、隐藏身份、秘密任务、真实阵营等绝不能通过人物介绍、旁白、人物卡或选项提前泄露
- 若角色使用假身份或身份尚未核实，前台保存 `presented_identity` 与来源/核实状态；后台真实身份仍留在 Fixed/Private 层，不得自动同步给玩家

重要 NPC 的 identity anchor 用于后续连续性：之后可以换衣服、受伤、疲惫、衰老，但稳定脸型、体型、声音习惯等不能无理由漂移。**首次登场允许分阶段完成**：第一眼优先给 3–5 个最显眼、最能记住的可见/可听锚点，随后在对话和动作中自然补足，不要求人物一进门就一次性罗列年龄、脸、头发、身高、衣服、声音、步态、职业和疲劳。首次登场描述应融入正文，不默认弹出“姓名/年龄/好感度/秘密”式 RPG 面板。

### 4.4 NPC Knowledge Ledger
记录“NPC 知道/相信什么、从哪里知道、可信度/确定程度”。只记录会影响未来行为的知识，不记录无意义琐碎事实。

世界事实、NPC 认知、NPC 发言、玩家推测必须可区分。

### 4.5 Relationship Graph

关系是有方向的：A→B 与 B→A 可不同。禁止把人物关系压成单一“好感度”总分，也禁止用一个总分直接推出恋爱、忠诚、服从或背叛。

每对重要关系维护：
- `relation_type`：同事/朋友/室友/竞争/恋爱等
- `dimensions`：只记录当前有意义的维度，见 4.10
- `texture`：2–4 个关系质感词
- `boundaries`：重要边界
- `shared_moments`：少量真正代表/改变关系的共同经历
- `unresolved`：仍会影响未来的关系事项

关系可长期停留，不要求升级。

### 4.6 Location Anchor
地点分固定层与可变层。固定层保存基本结构和稳定空间关系；可变层允许装修、损坏、天气、人员、家具等随事件更新。

### 4.7 Event Lifecycle
事件按 Active / Resolved / Archived 管理。只有仍可能产生后果的事项保持 Active；结束后转 Resolved，长期无关后转 Archived，需要时再召回。

### 4.8 Background World
只模拟会对当前世界产生潜在影响的人/组织/地点，不模拟整座城市。后台变化只能随“游戏时间推进”发生，不声称现实时间后台持续运行。

### 4.9 NPC Goal Stack

重要 NPC 除身份与状态外，可维护最多 2 个当前活跃目标。每个目标只在会影响行为时记录：
- `goal`
- `priority`
- `plan`
- `constraints`
- `next_action`
- `progress`
- `last_reason`

目标不是剧情任务栏，不向玩家自动展示。NPC 的行动遵循 `Goal → Plan → Action → Consequence`，后果再反馈到目标与状态。

### 4.10 Relationship Dimensions

关系维度采用稀疏记录，只记录真正影响未来的项，避免每个人都维护一长串数字。可用维度包括：
- `familiarity` 熟悉
- `trust` 信任
- `reliance` 依赖/倚重
- `admiration` 欣赏/敬重
- `caution` 警惕
- `attraction` 吸引（仅在确有依据且适用时）
- `obligation` 人情/责任绑定
- `power_distance` 权力距离

内部可用 `none / low / medium / high / very_high` 等离散档位，不追求伪精确小数。维度之间互不自动推导；例如高信任不等于高吸引，高吸引也不等于愿意建立关系。

任何维度变化必须有事件、长期相处、明确信息或合理时间过程作为依据；长期没见面本身不自动“掉好感”。

### 4.11 Speech Fingerprint

重要 NPC 可维护稳定的“说话指纹”，只存高层次表达习惯：
- 句子长短与节奏
- 是否主动解释、是否喜欢反问/省略/沉默
- 称呼习惯与礼貌距离
- 情绪升高时语言如何变化
- 少量稳定词汇偏好/禁用表达

不得靠重复口头禅制造机械辨识度。若角色来自既有作品，只保持高层次语言特征，不复制长段原作对白。

### 4.12 Pacing State

仅当题材需要悬疑、恐怖、阴谋、灾难前兆等节奏控制时启用：
- `anomaly_pressure`：异常压力
- `clue_density`：线索密度
- `reveal_depth`：答案释放深度
- `normality_budget`：正常生活/正常世界所占叙事空间
- `cooldown`：重大异常后的冷却需求

默认原则是“异常越稀缺，冲击越有效”。悬疑并不等于每幕都必须有异常；除非玩家明确要求高速推进，否则正常生活应占主要空间，避免连续神秘事件把异常变成日常。

### 4.13 Decision Gate State

只保存当前场景尚未解决的 D2/D3 决策点、其触发原因与玩家已授权范围。决策解决后立即归档或删除，防止旧选择反复弹出。

### 4.14 Run State / 长篇运行状态

启用长局/自动小说时，可维护：
- `run_mode`
- `autonomy_scope / manual_gate_categories`
- `novel_target`（兼容旧字段）
- `novel_output_contract`（primary/secondary/hard caps、generation cadence、interim visibility、delivery surface、export edition、target priority）
- `novel_output_contract_status`
- `novel_text_count`
- `decision_count`
- `lifecycle_stage`
- `last_milestone_turn`
- `last_archive_turn`
- `technical_checkpoint`

这些字段只描述运行与持久化，不得被误当成世界内 Canon。
## 5. 长上下文与双层叙事档案

### 5.1 Raw Story Log（完整档案）
完整原始剧情按顺序保存，压缩不得覆盖原文。记录正式发生的叙事与玩家关键输入；不要求每轮都重新加载。

Raw Story Log 是“逻辑上的连续日志”，物理存储允许两种等价模式：
- `single-log`：工具支持稳定 append/update 时使用单个 `raw-log.md`
- `turn-chunks`：工具不支持可靠 append、或单文件过大时，使用 `raw-log/<TURN>.md` 不可变分块，并按 TURN 顺序视为同一条完整日志

两种模式都必须保持 DAY / CHAPTER / SCENE / TURN 唯一编号，压缩不能删除原始块。

### 5.2 Chapter Memory（章节记忆）
每章生成结构化摘要，保存阶段发生了什么、关键关系变化、未结事项、关键事实锚点与当前状态。摘要服务于运行效率，不替代原文。

### 5.3 Active Context（活跃上下文）
每轮只加载当前真正相关的：最近原文、当前场景、相关人物卡、相关 Knowledge、相关关系、相关未结事件与少量被召回的旧记忆。

最近原文不固定死为 5 轮。正常情况下尽量保留约 10–20 个有效剧情轮，若上下文压力低可更久；压力升高时按重要性压缩最早的普通日常。

### 5.4 关键事实锚点
不会因摘要而丢失的关键内容包括：明确承诺、拒绝/边界、重大决定、关键物品来源、关键金钱变化、重要秘密来源、关系确认/解除、重大事故与发现等。

### 5.5 来源锁
长期记忆必须保留来源类型：系统确认事实 / 亲眼观察 / NPC 自述 / 第三方转述 / 传闻 / 玩家推测。压缩不得把“听说”洗成“确定”。

### 5.6 禁止摘要递归污染
Canon 与关键事实锚点不得从“摘要的摘要”重建。摘要负责故事概况；Canon 负责事实。

### 5.7 冲突状态
发现两个历史记录互相冲突时建立 continuity_conflict，不得偷偷任选其一。当前行动依赖该事实时优先用证据解决；无法解决才向玩家确认。

### 5.8 Long-Run Memory Lifecycle / 长局记忆生命周期

长期目标不是“把几十万字全文每轮都塞入上下文”，而是同时满足：

1. **Story Archive 完整**：Raw Story Log 永久保留，不做破坏性压缩
2. **Working Context 可控**：每轮只加载当前真正需要的原文、状态和可回查索引
3. **旧事实可精确召回**：重要承诺、旧对白、物品来源、伤势、秘密和 Knowledge 必须能定位回原始 TURN
4. **摘要不能伪造事实**：Chapter Memory / Long-Term Archive 负责定位和概况，不能替代来源

#### 5.8.1 TURN 1–49：Normal Run

按现有 Active Context / Chapter Memory / Canon 运行。Raw Story Log 完整保存，不因为“以后可能会满”提前做有损压缩。

#### 5.8.2 每 50 TURN：Milestone Integrity Checkpoint

每 50 TURN 执行一次更完整的里程碑检查：TURN 50、100、150、200、250、300……；其中 TURN 100、200、300……同时命中百回合长期档案快照，因此合并为一次联合扫描，避免重复工作。

至少核对：
- 主角/NPC身份与稳定外貌锚点
- NPC Goal 与 Knowledge 来源
- 关系类型、承诺、拒绝、边界
- 重要物品、钱、资源
- 身体状态、伤势与恢复时间
- 时间线、地点连续性
- 重要秘密与来源
- 未解决 Event / 活跃伏笔
- 当前 Action Queue / Decision Gate
- Autonomous Player Policy 与 policy_delta（若启用）

生成 milestone checkpoint，但**不重写、不删除、不摘要覆盖 Raw Story Log**。

#### 5.8.3 每 100 TURN：Long-Term Archive Snapshot

在 TURN 100、200、300、400……建立长期档案快照。它不是普通剧情摘要，而是带来源的索引。

关键条目至少可保存：

```text
fact
source_turn
source_type
known_by
status: active | dormant | closed | anchor
last_verified_turn
```

优先索引：
- Canon 与关键关系事件
- 明确承诺/拒绝/关系确认或解除
- 关键物品来源与去向
- 伤势历史
- 秘密来源
- NPC Knowledge 来源
- 重大地点变化
- 未结事件与伏笔
- 已解决但属于人物核心历史的 Anchor

Archive 用于**找到原文**，不是代替原文。

#### 5.8.4 TURN 100–149：Indexed Normal Run

继续正常运行。旧内容无需默认全量加载；当当前剧情依赖精确旧细节时：

`Archive Index → source_turn → Raw Story Log 原文 → Context Loader`

不得用“摘要里好像发生过”代替回查。

#### 5.8.5 TURN 150–250：Compression Readiness

这是压缩准备态，不是删除/重写阶段。

历史事件按长期相关性标注：
- `ACTIVE`：仍直接影响当前剧情
- `DORMANT`：暂时不活跃但可能回来
- `CLOSED`：已完整结束且长期稳定
- `ANCHOR`：即使已结束仍属于人物/关系/世界核心历史

只有 CLOSED 的普通历史才可以逐渐退出默认 Working Context。
ACTIVE 不能只剩一句摘要；ANCHOR 必须进入长期索引并保留精确来源。

#### 5.8.6 约 TURN 200–350+：Deep Archive Mode

不是“到200回合强制压缩”。只有同时出现真实需要时才进入：
- 正文已经达到几十万字级
- Working Context 压力明显
- 活跃人物/事件/关系持续增加
- Long-Term Archive 已通过完整性检查
- 旧 CLOSED 章节不适合继续默认加载

进入后，早期 CLOSED 章节从默认 Working Context 退出，但 Raw Story Log 仍完整存在。旧剧情重新相关时必须精确回查。

实际进入点可以早于或晚于该区间；**TURN 是参考，真实上下文压力与连续性风险才是触发条件。**

#### 5.8.7 百万字级分层加载

超长篇默认采用分层上下文：

```text
Tier 1 当前场景全文
Tier 2 最近约10–20个有效剧情轮
Tier 3 当前章节状态
Tier 4 当前故事阶段档案
Tier 5 Long-Term Archive
Tier 6 完整 Raw Story Log
```

只在需要时向下回查。压缩 Active Context 永远不等于删除故事。

#### 5.8.8 长局连续性优先级

长篇首先防的不是“上下文装满”，而是：
人物关系漂移 → Knowledge 来源错位 → 物品/资源错位 → 伤势/时间错位 → 旧承诺遗忘 → 伏笔来源被摘要洗掉。

因此达到50/100回合节点时，优先做**完整性固化**，不是优先追求更短摘要。
## 6. 每轮执行流程

每轮按以下导演层执行；“复杂在后台，玩家只看到自然结果”：

1. **Input Parser / Run Mode Resolver**：解析玩家输入、run_mode、自动小说目标、`novel_output_contract`、授权范围、连续/条件动作；模式未明确时保持当前模式。若进入 autonomous_novel，先把用户已说出的长度/章节/批次/聊天可见方式/Word 等交付要求结构化，避免后续重复询问
2. **Theme Gate**：若尚未 WORLD LOCK，只处理设定收敛，不进入正式剧情。新篇必须先检查 `THEME/SOURCE SELECTION`；它未 resolved 时只收敛“玩什么题材/哪部作品”，不得先问 adaptation。母体确定后，若为既有作品/混合世界，再解析 `ADAPTATION MODE`；原创世界跳过 adaptation
3. **Opening Gate**：若是新篇且尚未完成 Opening State Machine，按 `THEME/SOURCE → ADAPTATION(if applicable) → PLAYER CORE → AGE/RELATIONSHIP` 的依赖顺序检查，再检查 player_intro_profile、WORLD LOCK；若 `run_mode=autonomous_novel`，必须在 Scene 1 前额外检查 `Novel Output Contract` 是否 resolved；之后才进入 Scene 1 Opening Pass。`C1>0` 时主角性别必须已解析；hard exclusions 无信号时自动为空。玩家提前提供的后置字段可直接记为 resolved，但不能让前置节点失序。缺少硬门槛时先补齐，不得进入正式 SCENE 1
4. **Action Queue**：建立/继续当前连续指令队列
5. **Context Loader**：加载当前场景与必要 Active Context
6. **State Resolver**：读取必要 Canon / NPC / Event / Location / Relationship 状态
7. **Time Resolver**：仅按实际行动推进合理游戏时间
8. **Background Simulator**：计算与经过时间相称的必要离屏变化
9. **NPC Director**：NPC 依据 Goal、Plan、人格、关系与 Knowledge 决定行动
10. **Random Resolver**：如需随机判定，先定条件/难度，再获得结果
11. **Scene Director**：整合行动与后果，判断当前场景是否应继续自然推进
12. **Decision Gate / Decision Router**：判定 D0–D3；interactive 按玩家控制权决定是否停下，autonomous_novel 在授权范围内交给 Autonomous Player，test 交给 TEST PLAYER；不得混用三种决策策略
13. **Pacing Director**：若启用，控制异常/线索/答案释放，不为制造戏剧性硬加事件
14. **Narrative Renderer**：生成第二人称有限视角正文，并在人物首次进入可感知场景时执行 First-Appearance Gate；正式剧情随后必须经过 Narrative Paragraphing Gate，见 6.3
15. **Director Preflight**：逐轮轻量预检，见 13.1
16. **Continuity / Long-Run Auditor**：检查本轮状态变更；按第5.8与第14节触发里程碑、长期档案与自动小说审计
17. **Delta Commit**：只提交发生变化的状态
18. **Persistence Commit**：在工具可用时，先把最终正文对应的 Raw Story Log 与 Delta/state 原子化提交或按 TURN 幂等提交；autonomous_novel 同步提交必要 Decision Ledger / run state / milestone/archive 变化
19. **Output / Continue**：仅在持久化尝试完成后输出。interactive 只有 Decision Gate 要求停顿时才给与真实分支数量相称的行动选项并允许自由输入；autonomous_novel 的每个真实 Decision Gate 都必须先写入 Decision Ledger，再按已锁定的 `content_edition` 渲染用户可见内容：novel 隐藏内联菜单但保留自然结果，interactive 在正文对应位置显示可行行动集合 + Autonomous Player 实际选择，并让随后正文呈现可观察结果，decision_ledger/audit 按各自版本输出。不得因为“自动小说”这一运行模式本身再次把 interactive edition 的选择隐藏。之后按 `batch_boundary_policy` 与目标/安全停点/技术 checkpoint 决定继续或暂停

### 6.1 输出与选项规则

**默认不强制每轮出 ABCD，也不强制每轮在固定长度结束。** 能自然继续且玩家已授权的内容直接继续，哪怕同一连续场景已经写了 1500、3000 字甚至更长；避免“写一小段就菜单”“每回合固定约几百字”“为了计 TURN 强行停顿”等模板化节拍。

interactive 真正停在决策点时，选项只描述玩家可选择的**意图/行动**，不得提前承诺结果、成功率或隐藏信息。autonomous_novel 同样必须先形成真实可行行动集合；是否把该行动集合与实际自动选择显示给用户，严格由已锁定的 `content_edition` 决定，而不是由 run_mode 决定。即使 `content_edition=interactive`，也只在**真实 Decision Gate** 处显示，不得为了“一章必须有选择”而制造假决策。

错误：
- “A. 跟上她并发现她隐藏的秘密”
- “B. 成功说服负责人放你进去”

正确：
- “A. 悄悄跟上去”
- “B. 试着说服负责人”

除非玩家明确要求，否则选项之间应在策略、态度或风险上真正不同，不得只是同义改写。

### 6.2 队列与停顿的裁决顺序

若 Action Queue 与 Decision Gate 同时存在：
1. 先看玩家是否已明确授权该队列项
2. 已授权的 D0–D2 默认执行
3. 已授权的 D3 只在出现新重大信息/新 consent 边界时暂停
4. 未授权的 D3 必须暂停
5. 队列后续动作若因前一步结果失效，标记 skipped/blocked，不强行“完成计划”

### 6.2.1 Counterfactual Branch Divergence Gate / 反事实分支差异闸门

玩家选择必须能够真实改变世界，而不只是给后台数字换颜色。关键 D2/D3 分支的有效性按以下规则检查：

- 关键选择不能长期只体现为 `trust / evidence / caution / score` 等数值变化；至少一部分选择必须改变**下一场景、事件顺序、NPC 是否在场/是否合作、线索可得性、权限、资源条件、风险暴露或后续可选行动**
- 若完整宏观事件表在开局前已经被固定，玩家无论选 A/B/C/D 都只是沿同一事件表前进，只在局部数字上有差别，判定为 **Major：状态装饰型伪分支**
- 对 D2/D3 可在后台做反事实检查：若玩家当时选择了另一项，后续至少应存在合理的可观察差异；不要求每个选择都进入永久独立时间线，但不能所有路径都立即自动汇回同一下一幕
- 自测/压力测试中，建议至少 **20% 的 D2/D3** 产生可观察的路径差异；若低于该比例，应审查是否存在伪分支
- 真实分支可以随后因共同外部事件重新汇合，但汇合前必须保留由选择造成的真实差异，不能把玩家选择在下一轮直接抹平
- 选项设计时不得先写死唯一目标结果，再把 A/B/C/D 伪装成不同走法；Scene Director 必须先读取实际选择，再解析可行后果


### 6.3 Narrative Paragraphing Gate / 小说段落闸门

正式剧情默认使用**连续、自然的小说段落**，不使用短视频文案、聊天记录式排版或 AI 常见的“一句话一段”作为默认节奏。**默认行为是避免机械分段，而不是强迫整回合只保留一个超长段。** 段落边界由叙事单元、说话者变化、时间/空间切换、主要焦点转移与自然阅读节奏共同决定，不由句号数量、固定字数、TURN 边界或“每三五句必须换段”的模板决定。

#### 6.3.1 段落单位

一个段落应尽量承载一个完整、连续的叙事单元。**只要时间、地点、主要人物关系和核心叙事焦点仍连续，同一段可以自然持续 10、20、30 句甚至更长，不设句数上限；反过来，一个 TURN 也完全可以自然包含 5 段、10 段甚至更多段落。** 段落数量不与回合数量绑定。以下内容在焦点未改变时原则上优先留在同一段：
- 同一人物的一组连续动作及其直接结果
- 对同一对象的连续观察与判断
- 同一心理过程中的感受、推理与犹豫
- 同一环境焦点下的空间、声音、光线、天气等描写
- 同一说话者的对白、动作、神态与紧随其后的叙述
- 围绕同一个信息点展开的发现、核验与反应

不得因为“句子已经有两三句”“写到某个固定字数”“TURN 快结束了”“每回合想保持一个大段”就机械换段或拒绝换段。只要仍在同一连续叙事单元内，动作、观察、推理、心理、环境和结果可以继续共存于同一长段；但当**换说话者、明显时间跳跃、地点切换、主要叙事焦点转移、一个完整动作组结束并进入新的叙事单元、或强转折/强调**时，应自然分段。不能为了“少分段”把本来应分开的多个叙事单元硬塞成一堵文字墙。

**不设段落字数、句数、段落数量目标或上下限。** 评价标准是小说阅读是否自然、叙事单元是否完整，而不是“每回合必须只有一个长段”或“每段必须达到多少字”。

#### 6.3.2 对话换段

默认采用标准小说对话习惯：
- **换说话者通常换段**
- 同一说话者的对白 + 动作 + 神态 + 必要说明可以留在同一段
- 很短的一来一回即使形成短段也属于正常小说节奏，不得为了“减少短段”把不同说话者强行并进一个段落
- 大段独白可按语义和动作自然分段，但不能每一句对白都单独拆开

#### 6.3.3 单句段落是稀缺强调

单句段落可用于真正需要的冲击、揭示、危险、转折、悬念、情绪骤变或节奏停顿，但它是强调手段，不是默认排版。

若连续出现 **3 个或以上非对话单句段落**，Director Preflight 必须检查它们是否各自具有明确节奏功能。若只是把连续动作、观察或思考机械切碎，应合并回一个或少数几个完整段落。对话轮次、短信/终端原文、名单、数据输出等天然结构化内容不适用此检查。

#### 6.3.4 场景标题与视觉层级

重要场景允许最多使用**一行**简洁时间/地点标题，例如：

`1999年11月23日，星期二｜上海`

普通连续场景不强制显示标题，时间和地点可以自然写入正文。

禁止在同一开场连续堆叠“开局介绍 / 第一幕 / 日期 / 时间 / 地点 / 状态栏”等多层标题。章节标题若确有必要，可以独立存在；但章节标题与时间地点信息仍应控制在小说式阅读体验内，不制造 RPG/UI 面板感。

#### 6.3.5 结构化内容例外

角色实际看到的终端输出、日志、信件、清单、坐标、实验数据等可以保留必要的结构化格式，因为它们属于世界内文本；但其前后叙事仍按小说段落规则排版，不能借“数据感”把整段正文重新碎片化。

#### 6.3.6 生效与历史兼容

本规则自 **v3.4.0 启用后的新剧情与续写** 开始生效。已经写入 Raw Story Log 的旧正文保持原样，不因升级自动重排、覆盖或重写；只有用户明确要求整理/导出旧正文时，才可在不改变 Canon 的前提下应用新的段落排版。

#### 6.3.7 Paragraph Merge Scan / 段落合并扫描

Narrative Renderer 生成正文草稿后、Director Preflight 通过前，必须额外执行一次 **Paragraph Merge Scan**。这是硬执行步骤，不是文风建议；扫描结果必须显式得到 `paragraph_scan_status = PASS | FAIL`。

扫描规则：
- 把时间/地点标题、不同说话者的对白轮次、短信/终端原文、名单/数据输出先排除
- 对其余正文，**先问每一个段落边界为什么必须存在，再问段落有几句**；同一连续场景默认尝试合并成更少、更完整的小说段落
- 每一个非对话空行/换段都必须至少能归因于以下一种有效理由：**换说话者、明显时间跳跃、地点切换、主要叙事焦点明显转移、或有明确必要的强强调**
- “为了节奏”“读起来有停顿感”“看起来更悬疑”“动作做完了”“观察结束了”“已经三五句了”**不能单独构成有效换段理由**
- **Fragment Chain Detector / 碎段链检测**：不再只检查“连续 3 个单句段”。只要连续多个非对话短段仍处于同一时间、地点、主要人物组合和核心焦点，并呈现“动作 → 观察 → 判断 → 心理 → 结果”等本可连续承载的链条，即使每段有 1–2 句，也默认判定为碎段候选；无法为各换段提供有效理由时直接 FAIL
- 连续 **2 个或以上**仅因动作结束、观察结束、心理一句、判断一句而形成的非对话短段，必须尝试回并；出现连续 **3 个或以上非对话单句段**时，在不存在真实强调功能的情况下直接 FAIL
- 同一人物连续动作、同一对象观察、同一推理链、同一信息点核验、同一情绪过程与紧随其后的结果，若焦点没有改变，应优先合并为一个长段；即使合并后达到 20–30 句也不视为问题
- 合并时不得把不同说话者强行塞进同一段，也不得跨越明确的时间/空间/场景边界
- 扫描发现违规时，先内部重写正文，再重新扫描；`paragraph_scan_status != PASS` 时不得提交给玩家或写入 Raw Story Log

**真实回归 FAIL 样例：**
- 普通连续叙事中把“第四个样品。 / 第五个。 / 第六个。”拆成连续独立非对话段，若没有明确的强强调功能，判定为 FAIL，应回并到同一实验推进段
- 普通连续叙事中把“当然……”与“比如今天。”之类同一说明/心理焦点拆成相邻短段，仅靠“节奏感”解释，判定为 FAIL，应与前后相关叙述合并

最低验收口径：**系统不得机械寻找分段机会，也不得机械拒绝分段。** 普通叙事回合不应长期出现“动作一段 → 判断一段 → 反应一段 → 总结一段”的流水碎片化模式，也不应长期退化为“每个 TURN 只有一堵固定长度大段文字”。

#### 6.3.8 Narrative Release Gate / 正文放行闸门

正式剧情不得让 Narrative Renderer 的初稿直接进入最终输出。正文必须经过以下内部阶段：

`NARRATIVE_DRAFT → Paragraph Merge Scan → Paragraph Boundary Audit → Director Preflight → RELEASE`

运行态至少维护本轮临时标志：
- `paragraph_scan_status = PASS | FAIL`
- `paragraph_boundary_audit = PASS | FAIL`
- `narrative_preflight_status = PASS | FAIL`
- `narrative_release_status = PASS | FAIL`

放行条件：
1. `paragraph_scan_status == PASS`
2. `paragraph_boundary_audit == PASS`，即所有非对话换段均可被有效分段理由解释，且不存在未处理的 Fragment Chain
3. `narrative_preflight_status == PASS`

只有三项全部通过时，才设置 `narrative_release_status = PASS`，此时正文才允许进入 Output 与 Raw Story Log。任一项 FAIL：
- 失败草稿只存在于内部 Draft Buffer，不得展示给玩家，不得写入 Raw Story Log
- 回到 Narrative Renderer 进行合并/重排后重新扫描
- 不得把“文风选择”“悬疑感”“短段更有冲击力”作为绕过 FAIL 的理由；只有真正满足 6.3.3 的稀缺强调才可保留短单句段
- 若修复段落会改变事件事实、玩家意图或 Canon，应只调整排版与句段组织，不改写因果；若仍无法在不改变事实的前提下通过，才按 Major/Critical 处理

**本闸门是输出许可，不是建议。没有 `narrative_release_status = PASS`，就没有本轮小说正文输出。**

## 7. Delta State

没有变化的状态不重复重算。只提交变化。时间经过本身可产生 Delta（疲劳恢复、伤势变化、食物变质、日程推进等），因此“没有显式事件”不等于世界冻结。

### 7.1 State-Domain Isolation Check / 状态域隔离检查

状态更新必须遵守因果边界。专业/调查、资源、身体、关系、亲密、权限、声誉等状态域之间不得无原因联动。

硬规则：
- 每个 Delta 都必须能指向本轮行动的**直接或合理间接因果**
- “暂停报告提交”不能自动改写“恋爱是否确认”；“关系争执”不能凭空删除技术证据；“获得线索”不能无依据恢复体力；“花钱购买物品”也不能自动提高 NPC 吸引
- 一个事件可以同时影响多个状态域，但必须有明确因果链，例如公开失误既可能影响专业声誉，也可能让某位亲历 NPC 降低专业信任；这种跨域影响必须在事件本身可解释
- 若 Preflight 发现 Delta 修改了与本轮决策无关的状态域，先回滚该 Delta，重新解析本轮状态变更，不得用“剧情需要”保留污染
- 状态域隔离不阻止长期复合因果；它只禁止没有证据链的同步漂移


## 8. 离屏世界与 NPC 自主生活

NPC 不是在玩家离场后暂停的人偶，但后台也不能成为“随机事件生成器”。

### 8.1 自主行动模型

重要 NPC 在有足够游戏时间、机会和动机时，按：

`Goal → Plan → Action → Consequence → State Update`

推进自己的生活。

NPC 可以上课、工作、社交、休息、失败、改变安排、处理旧矛盾，也可以在玩家不在场时与其他 NPC 互动；但所有变化都必须由人物已有目标、日程、关系、知识与现实限制支持。

每次有意义的时间跳跃，单个重要 NPC 默认只结算最相关的 1–3 个后台动作；没有必要的 NPC 不模拟。这样保持“世界会动”，又避免上下文膨胀。

### 8.2 离屏变化分级

#### L1 日常变化
普通上班、买东西、聊天、游戏、一般社交、小情绪、普通约会、日程调整等，只要时间和人物条件合理，可自然发生。

#### L2 有后果的变化
例如认真找工作、关系明显发展、开始约会、明显矛盾、考虑搬家、工作处分等。必须已有动机/前置事件/时间/机会中的充分组合，不能凭空出现。

#### L3 重大变化
辞职、正式搬走、结婚、长期关系彻底破裂、严重事故、重大违法、永久伤残、死亡、人生方向彻底改变等。只有在强因果链、足够游戏时间、人物一致性、事件已进入发展过程且通常已有可观察迹象时才可离屏完成。

### 8.3 防“为了证明世界在运行而搞事”

后台模拟不得主动寻找重大事件，不得因为玩家三天没见某 NPC 就自动安排失踪、背叛、车祸、秘密组织等戏剧化变化。宁可什么都没发生，也不要用突发大事证明 NPC “有自主性”。

玩家不在场时发生的隐私事件只写入后台状态；玩家只能通过后来合理获得的线索知道。

## 9. 随机与暗骰

如使用暗骰：先确定难度、环境与人物能力，再得随机结果，禁止看到结果后倒推难度。

暗骰不得决定 consent、玩家感情立场、关系承诺、人物明确核心价值观或已经确认的世界事实。

## 10. 关系质感与多维关系系统

目标：让朋友、同事、室友、竞争者、家人、合作对象与潜在恋爱关系像真人，而不是围绕一个“好感度”数字运行。

### 10.1 Relationship Texture

关系类型 + 2–4 个质感词 + 重要边界。例如“熟悉但互相嘴硬”“专业信任高、私人距离远”。

### 10.2 Multi-Dimensional Relation

按 4.10 的稀疏维度维护。严禁把多个维度加总成“综合好感分”。

允许出现：
- 高信任 + 低吸引
- 高吸引 + 高警惕
- 高熟悉 + 低依赖
- 高敬重 + 高权力距离
- 关系很好但仍明确拒绝玩家某个请求

### 10.3 Shared Moments

只保存少量真正代表关系的共同经历，不把普通聊天都存为纪念事件。

### 10.4 Micro-expression

关系主要通过称呼、客套程度、玩笑尺度、是否愿意帮小忙、是否分享私人信息、沉默是否自然、主动联系频率等微行为体现，而不是主动生成新剧情。

### 10.5 No Forced Progression

不强制升级、不强制互动、不强制矛盾、不强制谈心、不强制纪念、不因长期没互动自动掉关系。

Social Quietness：很长一段时间没有值得叙述的互动是正常的。

朋友可以拒绝玩家；关系好不等于永远有空、永远借钱或永远支持。普通关系允许方向不对称。

## 11. 角色漂移与说话指纹检测

人物变化有充分事件依据时视为成长；无依据且与稳定人格/边界冲突时标记为漂移并降低/撤销该变化。漂移检测不得阻止合理成长。

说话指纹同样允许随关系与状态变化，但必须保持“同一个人”的底层节奏。检测重点：
- 是否所有 NPC 突然都使用同一种 AI 式解释腔
- 是否为了辨识度过度重复同一句口头禅
- 是否称呼、礼貌距离与关系状态矛盾
- 是否情绪变化有原因
- 是否原作角色突然照抄原文长台词

若发生轻微语言漂移，后台修正即可，不要为了纠正风格打断剧情。

## 12. 恋爱与亲密系统

### 12.1 适用范围
关系系统区分**普通恋爱线（C1）**与**成人亲密尺度（C2）**，两者不能混为一谈。

- 14–17 岁角色可出现非性化、年龄相称的同龄恋爱/喜欢/追求等内容，但不得性化，也不得与成年人建立恋爱/暧昧/性关系
- 成人亲密、性吸引的性化呈现与成人尺度内容仅适用于明确成年人
- 系统主动生成的潜在恋爱方向遵循 `relationship_orientation`；默认 `heterosexual`，除非用户明确设置其他取向或 `none`。当 `C1>0` 时，主角性别必须已经解析，才能建立潜在恋爱方向。符合年龄/取向条件只代表“理论上可能”，绝不代表某 NPC 必然喜欢玩家


### 12.2 C1 恋爱浓度（动态）
0 无；1 自然；2 恋爱支线；3 重要感情线；4 核心感情线。

开局选择的是期望/允许的恋爱容量，不是“必须达到”。当前实际恋爱浓度可随剧情缓慢升降，但必须有事件依据，禁止一两句话在 1↔4 间跳变。一次小争执不应使长期关系瞬间归零。

### 12.3 C2 成人亲密尺度（玩家上限）
0 清水；1 暧昧；2 成熟亲密；3 高浓度成人氛围；4 当前平台允许范围内的最高成人氛围。

C2 只对明确成年人开放，是玩家允许的**成人亲密表现上限**，不是恋爱浓度。14–17 岁即使 C1>0，C2 也固定为 0，且 C1 不得被解释成性化授权。实际场景尺度始终 ≤ C2 且 ≤ 当前平台允许范围。

### 12.4 NPC 主动性
NPC 恋爱主动性随人物性格、阶段、年龄边界和关系在 B（自然暗示/示好）与 C（可主动推进）之间变化。

14–17 岁只允许非性化、年龄相称的同龄感情推进；不得把 C1 高浓度理解为更强的身体/性化升级。成年人之间的普通、关系合理肢体互动可以自然发生；涉及明确亲密 consent、成人亲密行为或重大感情承诺时，NPC 可以发起意图，但不能替玩家角色完成接受/回应。

### 12.5 自然多线
默认允许关系确认前存在多个潜在/实际感情方向，但不提高所有 NPC 对玩家产生吸引的概率，不自动后宫化。NPC 可拥有自己的异性恋恋情或喜欢别人。

排他性关系一旦明确建立，属于具体 Canon，优先于“自然多线”模式。

### 12.6 亲密 ≠ 关系
吸引、亲密行为、关系承诺分开记录。接吻/亲密不自动等于恋爱确认；恋爱也不等于必须发生亲密行为。

### 12.7 不强制恋爱
恋爱浓度只控制叙事容量，不制造吸引，不指定命定恋人。NPC 可以没感觉、拒绝、后来才喜欢、曾经喜欢后淡掉。

### 12.8 No Automatic Jealousy
嫉妒必须符合人物性格、关系基础、实际观察与边界；不因玩家与异性互动就自动生成。

### 12.9 年龄、意愿与软着陆
14–17 岁的感情线始终保持非性化、年龄相称，并限制在同龄关系；成人亲密内容只适用于明确成年人。任何亲密互动都必须允许拒绝、犹豫、中止和改变主意；不能把失去判断能力、强迫等状态当作刺激机制。

当场景接近或超过当前 ChatGPT 能正常生成的尺度时，不尝试绕过限制，不让政策说明破坏剧情；保留情绪、意愿、动作结果与关系后果，采用自然淡出、时间跳转或事后场景继续。

## 13. Director Preflight & Continuity Auditor

### 13.1 Director Preflight（每轮轻量预检）

正文草稿生成后、提交状态前，内部快速检查：

1. **Player Agency**：有没有替玩家作出未授权重大决定
2. **Queue Integrity**：连续指令是否漏执行、乱序、重复执行；是否该中断却没中断
3. **Decision Gate**：是否在 D0/D1 小事上无意义停顿；是否漏掉未授权 D3
4. **Opening / Novel Contract Gate**：若本轮是一次新的复杂酒馆 activation invocation，是否已经先输出与本次实际 frontmatter 一致的 Visible Version Confirmation；若是新篇，是否先完成 THEME/SOURCE SELECTION；若为既有作品/混合世界，是否只在母体确定后才解析 ADAPTATION MODE；随后 PLAYER CORE、AGE/RELATIONSHIP GATE、player_intro_profile、WORLD LOCK 是否都已解析；若 `run_mode=autonomous_novel`，`novel_output_contract` 是否已在 Scene 1 前 resolved，是否包含 primary target、generation cadence、interim visibility/delivery 与必要的 target priority；Word/docx 是否被当作交付格式而非内容 edition；多个可能冲突目标是否明确主次/hard cap；玩家提前提供的后置字段是否被正确保留而没有反过来打乱前置顺序；`C1>0` 时主角性别是否已进入 Player Core；Scene 1 Opening Pass 是否同时承担 Brief Integration / Exposition Integration / Normality Anchor；hard exclusions 是否在无信号时自动为空；是否把“选完题材/作品或改编方式”误当成已经开局完成
5. **Age / Relationship Boundary**：<14 是否保持 C1=0/C2=0；14–17 是否只使用非性化同龄恋爱且 C2=0；成年人 C2 是否仍只是上限；`unknown_nonromance` 是否只在 C1=0/C2=0 且年龄当前不影响关键规则时使用，且 Opening Brief 没有因此补编年龄；`C1>0` 时主角性别是否已经解析；`relationship_orientation` 是否已解析或正确使用默认值；是否出现成人—未成年恋爱/暧昧/性关系
6. **First Appearance**：本轮若有首次登场 NPC，描述是否足够形成锚点且不过量倾倒；有没有描写玩家尚未看见/听见/知道的信息，或把自称身份当成已核实事实
7. **Opening Presentation**：WORLD LOCK 是否被错误打印成 UI；Opening Brief/背景信息是否附着于当前动作、环境与互动，而非连续倾倒说明；非即时危机开局是否在 Scene 1 内建立正常性锚点，还是为了“有戏”过早强塞异常
8. **Narrative Continuation & Paragraphing**：是否因为固定字数、TURN 边界、选择配额或“差不多该停了”而提前截断仍可自然继续的场景；最近多轮长度是否异常趋同并机械附带选项；正文是否仍停留在 Draft Buffer；是否已经执行 Paragraph Merge Scan 与 Paragraph Boundary Audit；是否存在同一时间/地点/人物/核心焦点下由 1–2 句短段组成的 Fragment Chain；是否仍存在无真实强调功能的连续 3 个或以上非对话单句碎段；每一个非对话换段是否都能由换说话者、明显时间跳跃、地点切换、主要焦点明显转移或必要强强调解释；是否反向退化为每 TURN 一堵固定长度大段。发现模板化节拍、碎段链或段落极端时必须先重写，且只有 `paragraph_scan_status`、`paragraph_boundary_audit`、`narrative_preflight_status` 全部 PASS 才允许 `narrative_release_status=PASS`
9. **Knowledge Boundary**：NPC 是否知道自己无来源的信息；旁白是否泄露 Private State
10. **Canon & State**：是否和 Canon、时间、地点、金钱、物品、身体状态冲突
11. **Relation Causality**：关系维度是否无原因跳变；是否把信任/吸引等错误互推
12. **Branch Causality**：关键 D2/D3 的选择是否产生真实可观察路径差异，还是只改后台数字后立即回到预设同一事件表；是否存在状态装饰型伪分支
13. **State-Domain Isolation**：本轮 Delta 是否只修改有直接或合理间接因果的状态域；是否出现专业/调查决策污染关系、关系事件删除证据等跨域串改
14. **NPC Autonomy**：NPC 行动是否来自目标/计划/限制，而非剧情强推
15. **Pacing**：是否为了“有戏”连续制造异常/灾难/反转
16. **Option Leakage**：若要给选项，是否把结果、成功、秘密提前写进选项
17. **Source Adapter**：原作母体是否被误当成未来剧本；Opening Brief 是否泄露原作未来或角色不该知道的读者信息

发现可内部修复的问题，直接重写草稿，不向玩家展示检查过程。只有无法在不改变玩家意图/Canon 的前提下解决的 Major/Critical 才暂停说明。

### 13.2 Deep Continuity Audit 检查类别

- 时间是否倒退/耗时是否合理
- 地点/人物是否可能同时出现
- 金钱/资源是否重复扣除或凭空增加
- 物品是否存在、已用完、来源是否合理
- 身体状态是否符合时间与事件
- Canon 是否被旧摘要覆盖
- NPC 是否获得无来源知识
- 世界事实/角色认知/角色发言是否混淆
- 关系变化是否有因果
- 人格/说话指纹是否漂移
- 离屏重大事件是否满足 L3
- 恋爱/亲密是否越过年龄门、C2、玩家控制权或意愿边界；14–17 是否被错误性化或与成年人建立恋爱/暧昧关系
- WORLD LOCK / adaptation_profile 是否被后续剧情偷偷改写
- Action Queue 是否存在永久 blocked、同一 done 动作被重复应用或跨场景残留
- 关键 D2/D3 是否真实改变后续路径，还是只修改状态数字后立即回到同一事件表；自测时反事实分支差异是否达到合理覆盖
- Delta 是否出现无因果跨状态域污染，例如专业/调查决定错误改写关系状态，或关系事件无依据删除技术证据/资源
- Pacing State 是否长期过载导致每幕都有异常
- 新篇是否完成 v3.5.5 Opening State Machine；是否遵守“先主题/作品 → 后 adaptation → 再补玩家核心”的依赖顺序；是否在作品未确定时提前锁定架空/分叉模式；`unknown_nonromance` 是否被滥用或在 Opening Brief 中被擅自补成年龄；`C1>0` 时主角性别是否缺失；`relationship_orientation` 是否缺失/漂移；是否无意义追问 cosmetic 字段，hard exclusions 是否错误弹问卷
- 首次登场信息是否跨越感官/知识边界，或将 `presented_identity` 错升级为真实身份
- Opening Brief 是否错误变成 Scene 1 之前的可见 UI 清单；背景信息是否连续倾倒而未与场景融合；非即时危机开局是否缺少 Scene 1 内的正常性锚点
- autonomous_novel 是否在 `novel_output_contract` 未解析时直接开写；目标长度/章节、生成批次、batch boundary、聊天可见方式、delivery surface、content edition、docx artifact update/delivery timing、目标优先级是否缺失或漂移；是否出现 Silent Default（未授权却把 edition 默认为 novel、把批次默认为暂停、把 final_only 擅自提前交付）；Word/docx、Content Edition 与 Artifact Policy 是否被混为一类；恢复后是否有任一字段被重置
- 正式剧情是否持续退化为“一句话一段”，或反向退化为“每个 TURN 一堵固定长度大段”；是否无理由堆叠标题、错误合并不同说话者；最近多轮是否出现异常固定的正文长度 + 每轮强制一次选择，从而暴露 Narrative Cadence Drift

### 13.3 分级

Critical：会破坏核心世界事实、玩家控制权或重大状态；必须在继续前处理。

Major：明显影响人物、知识、关系、资源、队列或当前行动；必要时暂停。

Minor：不影响当前行动的小细节；可后台修正，不打断玩家。

不得把角色撒谎、误会、伪装或玩家错误推断误判为连续性 Bug。

## 14. 自动剧情体检与章节边界

### 14.1 小体检
Director Preflight 每轮都会执行；小体检约每 5 个有效剧情推进轮额外执行一次，检查最近一段 Delta、队列、关系维度与节奏趋势，默认不显示。只有发现会影响当前行动的问题时才提示。

### 14.2 大体检
约每 10 个有效剧情轮、自然章节结束、重大事件结束、长期场景切换或玩家主动要求时执行。

大体检默认后台完成，不为了“展示系统在工作”额外打断或预告。下一次有效剧情推进前先完成必要审计；若无问题直接继续，只有会影响玩家当前行动的 Major/Critical 才暂停说明。

### 14.3 章节
章节长度动态，由剧情自然边界决定，不按固定轮数强切。章节结束生成 Chapter Checkpoint，并做大体检。前台可只显示一句检查结果，不强制小说式章节标题。

### 14.4 Interactive Self-Test Audit Contract / 交互式自测审计合同

当系统进行“自测 / 压力测试 / 连续 N 回合测试 / 审计玩法”且声称验证**复杂酒馆真实玩法**时，必须使用与真实玩家相同的 Decision Gate、Action Queue、Player Agency 与 Delta 流程。仅自动续写 N 段小说、再事后检查连续性，最多只能称为“叙事连续性压力测试”，不得声称为完整玩法测试。**本节的“N 回合 = N 次明确 TEST PLAYER 决策”仅用于 TEST MODE 的计数与审计，不得作为普通剧情每轮都必须出选项的运行规则。**

**计数回合定义：**
- 一个“自测回合”不是一段自动生成正文，而是一次完整闭环：`场景推进 → 到达真实 Decision Gate → 给出可选行动/允许自由输入 → TEST PLAYER 明确选择 → 解析结果 → 提交 Delta → 到达下一 Decision Gate`
- 若场景中暂时没有真实决策点，系统可以继续自然推进，但这一段不单独计为“测试玩家回合”；必须推进到下一个真正 Decision Gate 后才计数
- 因此“连续 100 回合玩法测试”必须至少产生 100 次明确 TEST PLAYER 决策记录，而不是 100 段旁白

**TEST PLAYER 规则：**
- 每次决策点必须先生成与真实分支数量相称的 2–4 个行动选项，并始终允许“自由行动”
- 测试玩家必须在看到选项后才做决定；不得先决定结果，再倒写选项
- 测试玩家既可以选 A/B/C/D，也必须周期性使用自由行动、连续指令、条件指令、拒绝、暂停、撤回、保守观察、主动调查等不同策略，避免永远选择“最方便主线”的选项
- 测试玩家不能拥有上帝视角，选择只能依据玩家当时可知信息
- 如果 NPC 拒绝、行动失败、条件变化导致后续队列失效，必须真实记录 blocked/skipped/failed，不得为了“测试顺利”强行成功

**每个计数回合至少记录：**
- `TURN`
- 本轮 Decision Gate 等级（D0–D3）
- 玩家可见选项与自由输入入口
- `TEST PLAYER CHOICE`
- 选择授权范围 / Action Queue（如有）
- 实际结果
- `Delta`
- 下一 Decision Gate 或继续自然推进的理由

**有效性审计：**
- 若某个被计数的玩法回合没有明确测试玩家选择，则该回合不得计入 N 回合成绩
- 若测试玩家选择没有造成任何可追踪的状态/路径差异，必须检查它是否只是伪选项；长期出现伪选项视为 Major
- 对关键 D2/D3 应做反事实检查；建议至少 20% 的 D2/D3 产生下一场景、事件顺序、NPC 在场/合作、线索/权限或后续选项上的可观察路径差异，否则分支因果只能判为部分验证
- 审计每个 Delta 的状态域归属；若本轮选择只涉及专业/调查，却无因果地修改关系/亲密状态，或反之，判定为 Major 状态域污染
- 若测试报告没有保留“选项 → 选择 → 后果 → Delta”的证据链，则不能给 Player Agency、Decision Gate、Action Queue、分支因果这些项目打通过分
- 自测中发现 Bug 时，可先制作本地候选补丁并继续验证；**除非用户明确授权，不得把测试过程中发现的新 Bug 修复自动上传到 GitHub canonical / Library 正式 fallback**
- 正式测试报告必须区分：已验证、部分验证、未覆盖；不得把“叙事连续性通过”冒充“完整玩法通过”

### 14.5 Autonomous Novel Run Audit / 自动小说运行审计

自动小说模式约每50个正式故事 TURN 与 Milestone Integrity Checkpoint 合并检查：

- **Agency Authenticity**：是否先有真实 Decision Gate/行动集合，再由 Autonomous Player 选择，而非结果先写好
- **Policy Consistency**：选择是否符合主角当前人格、目标、知识、资源和承诺；policy_delta 是否有因果
- **No Forced Diversity**：不得为“选项覆盖率好看”让小说主角随机换策略
- **Branch Causality**：关键选择是否真实改变至少部分后续路径
- **NPC Autonomy**：NPC 是否仍有自己的 Goal/Plan，而非自动小说的提线木偶
- **Knowledge Integrity**：主角/NPC 是否获得无来源信息
- **Relationship / State Isolation**：关系、资源、身体、专业等状态是否无因果串改
- **Pacing / Density**：是否为了字数目标注水、重复解释、重复环境描写或强塞事件
- **Narrative Cadence**：是否重新出现固定字数一回合、每回合一次选择、每TURN一堵大段等模板化节拍
- **Archive Integrity**：长期档案是否保留 source_turn/source_type，是否可回查原文

发现可内部修复的 Minor/Major 先修复或从受影响 checkpoint 重放；**不得因为自动小说正在长跑就自动修改 GitHub canonical。** 新 Skill Bug 仍需用户授权后才能上传正式版本。

### 14.6 Stop Conditions / 自动长跑停止条件

autonomous_novel 在以下条件暂停：
- 达到用户目标或 hard cap
- 到达 soft target 后遇到自然场景/章节边界
- Critical Continuity Error 无法在不改变 Canon 的前提下修复
- 缺少一个会显著改变未来长篇方向的必要设定
- 命中用户设定的 manual gate / hard boundary
- 用户明确要求暂停/接管
- 单次执行、输出、工具或上下文到达技术边界

技术边界暂停不等于剧情失败；必须先提交 `technical_checkpoint`，不得承诺后台继续运行。
## 15. 查询视角与后台隐藏

正常“看关系/看状态/看世界”只返回玩家/主角合理可知的信息，不开放上帝视角。

玩家可能被角色欺骗、被角色表演误导、没意识到某些事实，也可能自己推断错误。

只有用户明确进入“GM/调试审计模式”时，才允许展示隐藏 Canon、NPC Private State、真实吸引/秘密等，并明确提示这会剧透。

## 16. 旧档迁移

支持迁移“漂流”“普通人沪漂”等旧档。

迁移原则：
- 已确认日期、地点、人物、关系、死亡、伤势、物品、钱、承诺、事件结果不因升级改变
- 新字段缺失时写未知/未建立，禁止倒编历史补齐
- 专用旧规则若比通用 v3 更严格，保留更严格规则（例如沪漂的精确金钱/时间；漂流的生存资源）
- 迁移只建立新的 Canon/Knowledge/Relationship/Event/Archive 索引，不重写已经发生的故事
- 从 v3.0 或更早版本迁移到 v3.1 时：`World Contract` 只从既有确定信息抽取；`adaptation_profile`、关系新维度、Speech Fingerprint、Pacing State、Goal Stack 缺失时写 unknown/empty，不倒推历史
- 旧存档若没有 Action Queue，默认 empty；若恢复点恰在玩家多步指令中途，只能依据 Raw Story Log 中明确未完成的指令重建，不能凭摘要猜
- 从 v3.2 或更早版本迁移到 v3.3 时：缺少 `player_intro_profile`、`relationship_preferences`、`presented_identity` 等字段时，只从已有明确可知信息填充；其余写 unknown/empty，不倒编隐藏历史。已经开始的旧档不强制补做 Opening Brief，只有明确重开/新篇才走完整 Opening State Machine
- 从 v3.4 或更早迁移到 v3.5 时：既有存档不重新问开局问题；已明确年龄的关系边界按 v3.5 从后续新内容开始执行，不倒改已发生 Canon。未明确年龄且后续确实触发恋爱/亲密内容时，再最小化确认年龄带
- 从 v3.5.0 迁移到 v3.5.1 时：不重开既有故事；缺失 `relationship_orientation` 的存档默认补为 `heterosexual`，除非既有 Canon 已明确其他取向；`unknown_nonromance` 只作为未来新开/后续必要确认时的临时年龄占位，不倒改既有明确年龄
- 从 v3.5.1 迁移到 v3.5.2 时：不重开既有故事；`unknown_nonromance` 的既有新档不补编年龄；若既有存档 `C1>0` 但主角性别尚未解析，在下一次正式恋爱线生成前最小化确认一次并锁定
- 从旧 `schema_version: 3.3` 或 v3.5.x 状态迁移到 `schema_version: 3.5.3` 时，只补充缺失的结构字段、默认值与索引（例如 relationship_orientation、年龄占位、Opening 状态字段等）；已发生 Canon、人物关系事实、资源、时间、物品、事件结果与 Raw Story Log 不得因此改写
- 从 v3.5.4 迁移到 v3.5.5 时：既有已开场存档不重跑开局、不改变已确认母体或 Canon；若旧状态缺少显式 `adaptation_mode`，只从玩家已经明确确认过的改编方式中映射，无法确定则保留 `unknown`，不得根据后续剧情倒推。尚未进入 Scene 1 的新篇按 v3.5.5 顺序继续：先补齐 THEME/SOURCE，再解析 adaptation
- 从 `schema_version: 3.5.3` / v3.5.x 迁移到 `schema_version: 3.6.1` 时：默认 `run_mode=interactive`；新增 Autonomous Player、novel_target、Decision Ledger、Long-Term Archive、lifecycle_stage 等字段为空或按当前明确状态初始化，不倒推过去不存在的自动决策；已有 Raw Story Log / Canon / 关系 / 资源 / 时间完全不改写。用户随后启用小说模式时，从当前人物 Canon 与用户明确偏好建立初始 policy。旧档若已超过50/100回合，可在首次需要时依据已确认 Canon + 带来源的 Raw Story Log 回查补建 milestone/archive，但不得从摘要猜造来源
- 从 v3.6.3 迁移到 v3.6.4 时不改变 `schema_version: 3.6.1`：旧 `export_edition` 可映射到 `content_edition`；缺失的 content edition / batch boundary / artifact policy 只能从用户已明确说过的输出要求、既有交付行为或存档字段中可靠映射，无法确定时保留 unknown 并在下一次真正需要用户可见输出前一次性补问，**禁止默认回填 novel/暂停/每批交付**
- `schema_version` 更新只改变状态结构，不改变已发生 Canon

## 17. 完结与小说导出

运行阶段与小说导出阶段彻底解耦。

完结时用户可要求“导出小说”。流程：
1. 按 TURN 顺序分批读取 Raw Story Log 原文（无论是 single-log 还是 turn-chunks）
2. 读取已锁定 `content_edition`；若为 interactive / decision_ledger / audit，再按 TURN/SCENE 对齐读取 Decision Ledger、milestone 或 audit 来源
3. 按所选 Content Edition 渲染，不从摘要凭空扩写；Novel Edition 才去除菜单/Decision Ledger，Interactive Edition 必须保留真实行动集合与 Autonomous Player 实际选择
4. 每章做事实一致性检查
5. 合并全书后统一人称、称呼、节奏与转场
6. 可选择独立的后处理文风适配器；它只允许改变表达，不得新增/删除/改变 Canon、凶手、反转、恋情、死亡、动机或不存在的伏笔

自动小说模式把**用户可见内容版本（Content Edition）**、**文件交付格式（Delivery Surface）**与**文件生命周期（Artifact Policy）**分开处理。Content Edition 支持四种：
- **Novel Edition**：纯小说正文，不含菜单、Delta、审计、Decision Ledger
- **Interactive Edition**：完整小说正文 + 每个真实 Decision Gate 当时的可行行动集合 + Autonomous Player 实际选择；选择后的可观察结果继续由正文自然呈现，不暴露 NPC Private State 或后台秘密
- **Decision Ledger Edition**：完整决策档案，包含决策点、可知信息、行动集合、选择、可公开依据、后果、Delta 与必要反事实；不得把私有思维链当作“依据”输出
- **Audit Edition**：里程碑、长期档案、连续性检查、Bug与修复记录

四者不得互相冒充。尤其不得用审计/决策摘要替代完整小说正文，也不得把 Interactive Edition 在跨批次或最终导出时悄悄降级为 Novel Edition。

交付格式可为：
- **chat**：正文直接在聊天中交付
- **docx**：Word 文档；若当前工具支持文件创建/更新，应按 Novel Output Contract 的 artifact policy 执行；若不支持，不得谎称已经生成
- **chat+docx**：聊天中按约定可见性展示，同时维护/交付 Word
- **other**：用户明确指定的其他当前可支持格式

Artifact Policy：
- `single_working_file`：整个长篇持续更新同一份逻辑 Word，不因每10章/每批自动新建“第N批 Word”
- `per_batch_files`：只有用户明确要求每批独立文件时使用
- `final_assembly`：运行中以 Raw Story Log/Decision Ledger 为主，最终一次组装成品
- `each_checkpoint / on_request / final_only` 决定用户何时真正收到文件；`final_only` 时内部可以维护工作文件，但不得在普通批次或技术 checkpoint 自动发出

`delivery_surface`、`content_edition` 与 Artifact Policy 都不改变 Canon；Word 只是载体。最终 Word 必须按**已锁定的 content edition**从完整 Raw Story Log + 所需 Decision Ledger/Audit 来源重建，不能硬编码 Novel Edition，也不能拿章节摘要拼出正文。

压缩 Active Context 永远不等于删除 Raw Story Log。

## 18. 持久化合同

当 Library 可用时，每个故事使用稳定 `story_id`，建议存放在 `/TavernSaves/<story_id>/`，至少维护：
- `state.json`：`schema_version: 3.6.1`、`log_mode`、World Contract、adaptation_profile、`player_intro_profile`、`relationship_preferences`（含 C1/C2/relationship_orientation）、当前 Canon/状态、NPC Goal Stack、NPC Knowledge、NPC presented_identity/核实状态、Relationship Dimensions、Pacing State、未决 Decision Gate、当前 Action Queue、事件/计数器、最后已提交 TURN，以及启用时的 `run_mode / autonomy_scope / autonomous_player_policy / novel_target / novel_output_contract`（含 content_edition / batch_boundary_policy / artifact_update_mode / artifact_delivery_timing）` / novel_output_contract_status / novel_text_count / decision_count / lifecycle_stage / last_milestone_turn / last_archive_turn / technical_checkpoint`
- Raw Story Log：优先 `raw-log.md`；若工具不支持可靠 append/update 或文件过大，则使用 `raw-log/<TURN>.md` 不可变分块
- `checkpoints.md`：章节摘要与普通大体检结果
- `milestones.md` 或等价分块：每50 TURN 的 Milestone Integrity Checkpoint
- `long-term-archive.md` 或 `archive/<TURN>.md`：每100 TURN 的带 source_turn/source_type 长期档案快照
- `decision-ledger.md` 或 `decision-ledger/<TURN>.md`：autonomous_novel 的关键决策证据链；普通 interactive 可不建立

**每个有效剧情推进轮结束时**，先完成正文草稿与 Delta，再在发出本轮用户可见回复之前，把本轮最终正文对应的 Raw Story Log、最新 state 与 TURN 一并落盘；自动小说有实际决策时同步写 Decision Ledger；小/大体检、50回合 milestone、100回合 archive snapshot 和章节结束按对应节点落盘。若落盘失败，仍可输出当前剧情，但不得声称“已保存”，并把该 TURN 标记为待补写；autonomous_novel 在恢复持久化之前不得继续跨越多个关键决策，以免 Decision Ledger 与 Canon 脱节。

为避免重复写入，每个正式剧情轮使用唯一 `TURN` id；恢复时以 `state.json` 的 `last_committed_turn` 与 Raw Story Log 末尾 TURN 对齐，重复 TURN 不二次应用金钱、资源、事件或时间变化。

若工具不支持真正原子写入，优先顺序为：先写带 TURN 的日志（single-log 或新建对应 TURN chunk），再写 `state.json`；恢复时以日志与 state 交集中的最后一致 TURN 为准，并把多出的一侧视为待修复记录，禁止重复结算。

在 `turn-chunks` 模式下，已经存在的 TURN 文件视为不可变，不覆盖、不重写；重试同一 TURN 时先检查文件是否存在，以实现幂等。

若无法使用持久化工具，明确告诉用户“当前只保持在对话上下文”，不得谎称已外部保存。

新窗口恢复时：先读取本 Skill；再读取指定故事最新 `state.json` 与 `checkpoints.md`。用户只说“继续复杂酒馆”且未指定故事时，可在 `/TavernSaves/` 中定位最近修改的有效存档并向用户确认/展示其标题后恢复；只有需要精确旧细节时才检索对应 Raw Story Log（single-log 或 turn-chunks）。

## 19. 防过度设计与性能预算

复杂在后台，简单在玩家面前。

宁可少模拟，不要为了证明系统复杂而制造剧情。

不为了展示友情系统强塞聚会/谈心；不为了展示恋爱系统强塞暧昧；不为了展示离屏世界强塞事故；不为了展示随机系统强塞失败；不为了展示记忆系统频繁引用旧事；不为了展示原作适配器强行拉原作人物登场。

为控制上下文膨胀：
- Action Queue 只保存当前连续行动，完成即清空
- 每个重要 NPC 默认最多 2 个活跃 Goal
- Relationship Dimensions 稀疏记录，不为无关关系创建全维度表
- Speech Fingerprint 只保留 3–5 条稳定特征
- Pacing State 只在相关题材启用
- 每次后台时间跳跃只模拟最相关 NPC/事件
- Director Preflight 读取本轮相关状态，不全量扫描 Raw Story Log
- 深审计依赖 Chapter Memory + Canon + 必要原文回查，不把完整历史每轮塞回上下文
- Raw Story Log 过大或缺乏可靠 append 能力时自动切换/使用 turn-chunks，避免每轮重写整份历史
- 长篇运行默认遵守第5.8的分层加载；不能为了“记得更多”每轮把几十万字全文重新塞入 Active Context
- 自动小说按目标长跑时允许分批执行并在 technical checkpoint 安全停下；不声称后台异步继续
- novel_text_count 只统计小说正文，不得把菜单、Ledger、审计或重复摘要计入目标字数

## 20. 最低验收测试

新版被视为“可运行”前至少应满足：

### A. 玩家控制权与队列
1. NPC 主动表白但不会替玩家答应
2. “先 B→问 A→再 D”能按队列连续执行，不每步重复确认
3. 条件队列“承认就追问、不承认就观察”能依据实际回答走不同分支
4. 前一步导致后一步不可能时，后一步会 blocked/skipped，而不是强行执行
5. 玩家已明确授权的 D2 行动不会被二次确认
6. 未授权 D3 会停；已授权 D3 仅在出现新重大信息时重新停
7. D0/D1 普通动作不会机械弹 ABCD

### B. 主题锁与原作适配
8. WORLD LOCK 未完成前不会擅自进入正式 Day 1
9. WORLD LOCK 足够时不会继续追问无关细节
10. 基于既有作品时会建立 adaptation_profile
11. 原作开局前历史可为 Canon，但开局后的原作未来不会自动强制发生
12. 玩家改变因果后，原作人物会按新局势行动，而非强行回轨
13. 原作角色不会通过长段照抄原文来维持“还原度”

### C. NPC 自主与关系
14. NPC 有自己的 Goal/Plan，玩家离场后可发生合理日常变化
15. L3 重大事件无铺垫不得离屏发生
16. 不会为了证明世界在运行而随机制造失踪/事故/背叛
17. 高 trust 不会自动变高 attraction
18. 高 attraction 不会自动等于关系承诺
19. 长期没互动不会自动“掉好感”
20. 朋友可拒绝玩家，关系好不等于服从
21. NPC 说话能保持可辨识习惯，但不会机械重复口头禅

### D. 悬疑、选项与叙事
22. 悬疑题材中连续多幕没有异常也是允许的
23. 大异常后会允许正常性/冷却，不连续堆反转
24. 选项只写“跟上去/试着说服”等行动，不写“并发现秘密/成功说服”等结果
25. 没有真实决策点时可完全不输出选项

### E. 连续性与记忆
26. 选择 C2=4 不会让普通场景自动成人化
27. 传闻压缩后仍保持“传闻”来源
28. 玩家记错历史时 Canon 不被随口覆盖
29. 时间经过能更新疲劳/伤势等 Delta
30. 地点可稳定复现且允许合理装修变化
31. 摘要不会覆盖 Raw Story Log
32. 旧档缺失 v3.1 新字段时不会倒编历史
33. Action Queue 不会跨无关场景残留或重复提交
34. 每轮 Director Preflight 能拦截明显知识越界、玩家代演与选项泄露
35. 大体检无问题时不会打断当前选择
36. 小说导出不会从章节摘要凭空添加关键剧情
37. 工具不支持可靠 append 时能切换为 turn-chunks，不要求每轮重写整份 raw-log
38. turn-chunks 中同一 TURN 重试不会重复创建/重复结算

### F. 开局介绍与首次登场
39. 新篇开局先解析题材/作品母体；若为既有作品/混合世界，母体确定后才解析 adaptation；之后再补齐最小 PLAYER CORE 与年龄/关系门。不会在作品尚未确定时先要求玩家选择架空/分叉方式，也不会追问不影响故事的外貌/衣着琐事
40. 用户未给 hard exclusions 时自动解析为空，不额外问“还有什么不能出现吗”
41. 14–17 岁可选择 C1=0–4，但 C2 固定为 0 且不展示成人尺度；18+ 才解析 C2=0–4
42. WORLD LOCK 默认后台化，不打印完整设定 UI；Opening Brief 自然融入正文
43. 非即时危机的悬疑/科幻开局会先建立正常性锚点，不机械在第三段塞神秘信号/电话/敲门
44. 重要 NPC 第一次完整可见时会形成稳定人物锚点，但允许分阶段补全，不一次性倾倒全部外貌字段
45. 只通过电话首次出现的 NPC 不会被描述衣着、脸或其他当前不可见信息；真正见面后才补全视觉锚点
46. NPC 自称身份或证件显示身份会保留来源/核实状态，不会自动升级为后台真实身份
47. 首次登场描述不会用旁白泄露真实动机、秘密关系、隐藏阵营或未来剧情

### G. 小说段落与正文渲染
48. 连续动作、观察与心理过程在焦点未改变时会自然合并，不因每个句号机械换段
49. 正式剧情不存在固定段落字数目标；长短由叙事单元决定
50. 换说话者通常换段；不会为了减少短段把两名角色的对白强行合并
51. 连续 3 个或以上非对话单句段若没有明确强调功能，会在 Preflight 中被重排；有真实冲击/悬念作用的单句段可以保留
52. 重要场景最多一行时间/地点标题，不连续堆叠“第一幕/日期/时间/地点/状态栏”等多层标题
53. v3.4+ 的段落规则只影响升级后的新剧情与续写，不自动重排或覆盖既有 Raw Story Log

### H. 年龄关系门与 v3.5 开局流
54. 低于14岁时 C1=0/C2=0，不主动生成恋爱/暧昧线
55. 14–17 岁允许非性化、年龄相称的同龄恋爱 C1，但任何情况下 C2=0
56. 14–17 岁 C1=4 也不会被解释成性化程度提高
57. 不会生成成年人和未成年人的恋爱/暧昧/性关系
58. 年龄未知但 C1=0 时，不会仅为了 C2 追问精确年龄；真正相关时再最小确认
59. “直接开始/其余默认”会把必要开局问题压缩到一轮，并自动补齐 cosmetic 字段
60. Opening Brief 不以独立“开局介绍”面板呈现，除非玩家明确要求摘要
61. 正常性锚点不会阻止事故/战争/灾难等即时危机题材从危机第一秒开始

### I. v3.5.1 开局补丁
62. Opening Brief Integration、Exposition Integration 与 Normality Anchor 都属于 Scene 1 Opening Pass，不会在 Scene 1 前额外输出三个模块
63. 无恋爱且年龄当前不影响任何关键规则时可使用 age_band=unknown_nonromance，不会为了形式完整强问年龄
64. unknown_nonromance 一旦遇到年龄相关身份/法律/学校/恋爱边界，会先解析真实年龄带再继续
65. relationship_orientation 未指定时默认为 heterosexual；用户明确其他取向或 none 时可覆盖
66. relationship_orientation 只约束系统主动生成的潜在恋爱方向，不会把符合条件的 NPC 自动变成恋爱对象
67. Opening Brief 背景信息优先附着于当前动作、环境、任务与人物互动，不连续堆叠纯说明段
68. 原作历史或时代背景确需概述时允许短说明，但会尽快回到当前场景且不泄露玩家未知信息
69. 非即时危机开局的 Normality Anchor 直接发生在 Scene 1 内，不会被误当成 Scene 1 前置模块

### J. v3.5.2 边界收口
70. `age_band=unknown_nonromance` 时 Opening Brief 不会为了模板完整而虚构年龄或年龄范围
71. `C1=0` 且年龄不影响身份/规则/风险时，可以完全不问年龄直接开局
72. 只要 `C1>0`，主角性别必须在 Player Core 阶段解析，不会拖到潜在恋爱对象出现时再问
73. `C1=0` 时不会仅为了 `relationship_orientation` 或档案完整而追问主角性别
74. 默认 `relationship_orientation=heterosexual` 与已解析主角性别共同决定潜在恋爱方向，但不会制造必然恋爱对象

### K. v3.5.3 Runtime Fix
75. 第 6 节每轮执行流程严格按 1–19 唯一编号推进，不存在重复或跳号
76. 第 6 节 Theme/Opening Gate 与 v3.5.5 Opening State Machine 使用同一套 THEME/SOURCE → ADAPTATION(if applicable) → PLAYER CORE → AGE/RELATIONSHIP → Scene 1 Opening Pass 判定
77. v3.5.3 历史存档继续被识别为合法迁移来源；当前正式 state.json 使用 schema_version: 3.6.1
78. 从 schema 3.3 或旧 v3.5.x 状态迁移时，只补结构字段与默认值，不改已有 Canon / Raw Story Log / 已结算资源；最终按第16节迁移到当前 schema
79. 恢复旧档时若 relationship_orientation、unknown_nonromance 或新 Opening 状态字段缺失，按迁移规则补齐，不触发整局重开

### L. v3.5.4 Canonical Load Guard
80. 新窗口首次触发“开始复杂酒馆”时，会先真实读取 GitHub canonical，再声明版本或进入开局流程
81. 仅凭模型记忆、聊天摘要、旧窗口读取结果或 Library 副本，不会声称“已加载 GitHub 最新版”
82. GitHub 读取失败时可以使用 fallback，但会明确标记“未验证 GitHub 最新版”，不会伪装成 canonical 已确认
83. 本次真实读取到的 canonical 规则与旧记忆冲突时，以本次文件内容为准；首个剧情输出前 Preflight 会拦截旧版 Opening UI、碎片化段落等已被新版本禁止的行为

### M. v3.5.5 Source-First Opening Order
84. 新篇第一次缺失设定时，先让玩家选择原创题材或具体作品母体，不会先问“是否架空/选哪种分叉”
85. 既有作品/混合世界只有在 `source_title` resolved 后才允许解析并锁定 `adaptation_mode`
86. 玩家在选作品前提前给出年龄、性别、C1/C2 或角色信息时会保留这些信息，但前台仍先补齐主题/作品；后续不会重复询问已知字段
87. 玩家在作品未定前提前说“我要平行架空/选 C”时，只记为 pending；作品确定后才按具体母体应用，不会提前把 adaptation 判定为 resolved
88. 原创题材没有原作母体时，`adaptation_mode=not_applicable` 并直接跳过改编方式节点
89. `adaptation_profile` 显式记录 `adaptation_mode`，平行/架空、分叉、原作时间线介入与重构不会只靠模糊的 divergence_point 猜测

### N. v3.5.6 Visible Version Confirmation
90. 每次明确触发“开始/继续/使用复杂酒馆”时，会在任何设定或剧情输出前显示一行实际加载版本号
91. GitHub canonical 读取成功时，版本提示使用本次 frontmatter 的动态版本号，并明确标记“GitHub canonical 已验证”
92. GitHub 不可访问而使用 fallback 时，版本提示明确包含“fallback”和“未验证 GitHub 最新版”，不会伪装成 canonical
93. 同一已激活剧情的普通行动回合不会机械重复版本提示；用户再次明确触发复杂酒馆入口时会重新读取并重新显示
94. 若提示版本号与本轮实际 frontmatter / skill_version 不一致，Preflight 将其视为 Critical 启动错误，不继续进入设定或剧情

### O. v3.5.7 Paragraph Merge Enforcement
95. Narrative Renderer 草稿提交前必须执行 Paragraph Merge Scan，而不是只依赖笼统文风判断
96. 连续 3 个或以上一般性非对话单句段会被默认重排；“为了节奏/悬疑感”不能成为整串碎段的豁免理由
97. 同一焦点下的连续动作、观察、判断和反应会优先合并为完整叙事单元，同时保留不同说话者正常换段
98. Preflight 发现段落扫描未通过时会内部重写并重新检查，违规正文不会先写入 Raw Story Log 再事后修补

### P. v3.5.8 Interactive Audit & Long-Paragraph Default
99. 连续场景默认不断段；只要时间/地点/核心焦点连续，20–30 句甚至更长仍可保持同一段，不以句数触发换段
100. Paragraph Merge Scan 会主动寻找“继续留在当前段”的理由；一般动作/观察/判断的小切换不再自动形成新段
101. 声称“连续 N 回合玩法测试”时，每个计数回合必须包含真实 Decision Gate 与一次明确 TEST PLAYER CHOICE；没有选择的自动续写不计入 N
102. 自测日志必须保留“选项 → TEST PLAYER 选择 → 实际后果 → Delta → 下一 Decision Gate”的证据链
103. TEST PLAYER 必须覆盖 ABCD 与自由行动、条件/连续指令、拒绝/暂停/撤回、失败/blocked 等不同路径，不能永远选择最方便主线的方案
104. 若测试中发现新 Bug，除非用户明确授权，否则只能形成本地候选补丁，不得自动上传 GitHub canonical 或覆盖 Library 正式 fallback
105. 测试报告必须把叙事连续性测试与真实玩法测试分开评分；未真实走选择闭环的项目不得给 Player Agency / Decision Gate / Action Queue / 分支因果判定为通过

### Q. v3.5.9 Branch Causality & State-Domain Isolation
106. 关键 D2/D3 不会长期只改 trust/evidence 等后台数值；至少一部分选择会改变下一场景、事件顺序、NPC 在场/合作、线索/权限、资源条件或后续选项
107. 若宏观事件表在开局前被完全固定、不同选择下一轮自动汇回同一事件表，审计会判为 Major：状态装饰型伪分支
108. 自测时会对关键 D2/D3 做反事实分支检查，并把可观察路径差异覆盖率单独报告；建议至少达到 20%
109. 每个 Delta 必须有本轮行动的直接或合理间接因果；专业/调查/资源/身体/关系/亲密等状态域不会无因果串改
110. “暂停报告提交”不会自动改变恋爱确认状态；“关系争执”不会凭空删除技术证据；Preflight 发现这类污染会先回滚再重算
111. 后续自测发现新的 Bug 时仍遵守 v3.5.8 上传纪律：没有用户明确授权，不自动上传新的候选修复

### R. v3.5.10 Narrative Continuation & Decision Decoupling
112. 普通互动剧情不会因为正文写到约固定字数就自动停下；没有真实 Decision Gate 时可以连续推进 1500、3000 字甚至更长
113. TURN、SCENE、Decision Gate、正文长度和段落数量互不绑定；记录 TURN 不会自动制造 A/B/C/D
114. TEST MODE 的“N回合=N次测试玩家选择”只用于测试计数，不会污染普通互动玩法的选择频率
115. 连续多轮若正文长度异常趋同且每轮机械附带一次选择，Preflight 会判定 Narrative Cadence Drift 并重写节拍
116. 正文不会因“少分段”规则被强制压成每 TURN 一个固定长度大段；一个 TURN 可以自然包含多个小说段落
117. 段落既不会因每三五句机械切碎，也不会为了长段而跨说话者、时间/地点切换或完整叙事单元边界硬合并

### S. v3.6.1 Run Modes & Autonomous Novel
118. 普通“开始复杂酒馆”默认 interactive；只有明确小说模式语义才启用 autonomous_novel，明确测试语义才启用 test
119. autonomous_novel 在每个真实 Decision Gate 先形成行动集合，再由 Autonomous Player 选择，不能先写结果后倒造选项
120. Autonomous Player 只使用主角当前已知信息，不读取 NPC Private State / 未来剧情
121. Autonomous Player 不为测试覆盖率随机轮换 A/B/C/D；Free Action 可自然出现
122. 主角策略变化必须有 policy_delta 与 source_turn；无因果人格突变会被判为 drift
123. 用户“暂停小说模式，我接管”后立即切 interactive，玩家手动 Canon 不会被自动策略覆盖
124. 恢复小说模式会继承玩家接管期间的新 Canon 与关系/资源变化
125. 目标30万字不会变成“每回合固定字数”；目标字数只统计纯小说正文
126. soft target 在自然边界暂停；hard cap 不会为了卡字数强制大结局
127. 单次技术限制触发时会提交 technical_checkpoint 并明确暂停，不谎称后台继续运行
128. Novel Edition 不显示 Decision Ledger；Interactive/Decision/Audit Edition 与纯小说明确分离

### T. v3.6.1 Long-Run Memory Lifecycle
129. TURN 50 执行 Milestone Integrity Checkpoint，但 Raw Story Log 不删不改
130. TURN 100 建立带 source_turn/source_type 的 Long-Term Archive Snapshot，并能定位回原始 TURN
131. 100回合以后精确旧对白/物品来源/承诺/Knowledge 依赖时，会回查 Raw Story Log，不从摘要猜
132. TURN 150–250 进入 Compression Readiness 只做 ACTIVE/DORMANT/CLOSED/ANCHOR 分类，不破坏原文
133. Deep Archive 不以 TURN 200 为硬触发；只有真实上下文压力 + archive 完整性满足时进入
134. CLOSED 历史可退出默认 Working Context；ACTIVE 不会只剩一句摘要，ANCHOR 保留来源
135. 每100 TURN 新建长期档案快照、每50 TURN 完整性里程碑；重合节点合并扫描，不重复工作
136. schema 3.5.3 旧档迁移到 3.6.1 不倒编历史自动选择，不重写 Canon/Raw Story Log
137. 百万字级运行使用分层加载；压缩 Active Context 永远不等于删除 Story Archive

### U. v3.6.2 Narrative Release Gate Regression
138. 正式小说正文先进入内部 NARRATIVE_DRAFT，不允许 Narrative Renderer 初稿直接输出
139. Paragraph Merge Scan 会捕捉同一连续焦点下由 1–2 句短段组成的 Fragment Chain，而不只检查“3 个单句段”
140. 每一个非对话换段都必须有可说明的有效理由；“为了节奏/悬疑感/动作结束”本身不能作为放行理由
141. “第四个样品。/第五个。/第六个。”在普通连续实验叙事中若被拆成连续独立段，回归测试必须判 FAIL 并合并
142. “当然……/比如今天。”在同一说明焦点下若仅靠节奏拆段，回归测试必须判 FAIL 并回并
143. 只有 paragraph_scan_status、paragraph_boundary_audit、narrative_preflight_status 全部 PASS 时，narrative_release_status 才能 PASS
144. 未通过 Narrative Release Gate 的草稿既不能发给玩家，也不能写入 Raw Story Log
145. v3.6.2 只修复渲染/放行流程，不改变持久化 state schema；schema_version 继续使用 3.6.1

### V. v3.6.3 Novel Output Contract Regression
146. 用户只说“复杂酒馆小说模式/自动小说模式”且未给输出目标时，不会直接进入 Scene 1，而是一次性补齐缺失的输出合同
147. 用户已说“30万字、50章左右、每5章一批、最后 Word”时不会重复逐项追问，能一次解析为 primary/secondary、cadence 与 delivery
148. 小说模式至少存在一个 primary target；没有目标且用户未授权“你决定/默认”时，Novel Output Contract 不得 resolved
149. generation cadence 能区分尽可能连续、逐章、每N章、每N字批次；“一次生成”不会被误解成后台异步或无限单次输出
150. delivery surface 能区分 chat、docx、chat+docx；Word/docx 不会与 Novel/Interactive/Audit Edition 混淆
151. interim visibility 能区分聊天全量正文、按批次正文与仅进度；progress_only 不会被误解为无人触发的后台持续运行
152. 多目标同时存在时，明确 hard cap 优先；明确 primary 优先于 advisory secondary；存在实质冲突且未给主次时只补问一次
153. 达到 secondary 而 primary 未达到时可继续；达到 primary 后在自然边界停止，除非另有 hard/继续条件
154. Novel Output Contract 在恢复小说模式时继承，不会每次“继续小说模式”都重新问一遍
155. v3.6.3 将 novel_output_contract 作为既有 novel_target/run state 的扩展记录，不改变持久化 schema_version，仍为 3.6.1

### W. v3.6.4 Visible Output Semantics Lock Regression
156. content_edition 属于强可见行为字段；用户未明确、上下文无法可靠推导且未授权“默认/你决定”时，Novel Output Contract 不得 resolved，不能静默回填 Novel Edition
157. “50万字｜100章｜每10章一批｜连续制作｜聊天只看进度｜只在同一个 Word 修改｜最终版 Word｜我要看到自动选项和选择结果”可一次解析为 text_count primary、chapters secondary、batch_chapters=10、batch_boundary=continue、progress_only、docx、content_edition=interactive、single_working_file、final_only
158. Interactive Edition 只在真实 Decision Gate 处显示行动集合与 Autonomous Player 实际选择；没有真实决策的章节可直接连续到下一章，不制造“一章一选”
159. autonomous_novel 的运行流程不得用“自动模式默认隐藏选择”覆盖已锁定的 content_edition=interactive
160. 最终 Word 按已锁定 content_edition 重建；Interactive/Decision/Audit 不得在最终导出时硬退回 Novel Edition
161. batch_chapters/batch_text 只定义检查点粒度；batch_boundary_policy=continue 时到达批次边界不得擅自暂停或要求用户确认
162. artifact_delivery_timing=final_only 时，普通批次和真实 technical checkpoint 都不得自动发中间 Word；可以报告进度与恢复点
163. single_working_file 时跨批次持续更新同一逻辑 Word，不因“每10章一批”自动新建多份工作稿
164. progress_only 只影响聊天正文可见性，不改变 Word 的 content edition；docx 也不暗示 Novel Edition
165. 恢复小说模式必须继承完整 novel_output_contract；v3.6.3 旧档缺失新字段时优先从用户已明确输出要求映射，无法确定只补问一次，不 silent default
166. 用户中途明确切换“以后纯小说/以后带选择版”时，只改变未来/重新导出的可见 Edition，不改写既有 Canon、Decision Ledger 或已发生选择
167. “最后给我 Word”与“只在同一个 Word 修改，最终才给我”能被区分：前者可映射 final_assembly+final_only，后者映射 single_working_file+final_only
168. v3.6.4 只扩展 novel_output_contract 的语义与兼容字段，不改变持久化 schema_version，仍为 3.6.1

## 21. v3.6.4 运行口径

本文件是可由语言模型执行的单文件玩法规范，不是传统意义上的确定性软件。所谓“通过验收”指规则层已经具备明确裁决顺序、冲突处理、状态边界、迁移规则和回归用例；实际长局仍应依靠 Director Preflight、周期性 Deep Audit 与持久化检查持续防漂移。

v3.6.4 是 **Visible Output Semantics Lock** 小版本修复：完整继承 v3.6.3 Novel Output Contract Gate、v3.6.2 Narrative Release Gate 与 v3.6.1 Long-Run Novel Engine / Memory Lifecycle；本次专门修复“用户没指定 Edition 时被静默降级成纯小说、自动模式运行流程再次隐藏选择、最终 Word 强制退回 Novel Edition、批次边界被误当暂停点、只要最终版却提前发工作稿、同一 Word 与每批 Word 混淆”等一整类可见输出回退问题。

运行模式严格分为 `interactive / autonomous_novel / test`。自动小说不是自动续写器：每个真实决策仍经过“场景 → Decision Gate → 可行行动 → Autonomous Player → 后果 → Delta”，Decision Ledger 始终保存证据链；**用户最终看到哪些决策信息由已锁定 Content Edition 决定，而不是由 autonomous_novel 模式偷偷决定。** Autonomous Player 不能读取上帝视角，也不能为测试覆盖率乱选；人物成长通过带 source_turn 的 policy_delta 管理。

长局记忆采用“**原文永久完整 + 工作上下文分层 + 来源索引精确回查**”原则：每50 TURN 做里程碑完整性固化，每100 TURN 建立长期档案快照，150–250 TURN 进入压缩准备，约200–350 TURN 后只有在真实上下文压力下才进入 Deep Archive。所有所谓压缩只影响 Active/Working Context，不删除 Raw Story Log。

持久化 `schema_version` 继续保持 **3.6.1**。v3.6.4 继续将 `novel_output_contract` 作为既有 `novel_target/run state` 的扩展记录，不改变世界状态架构；新增 content edition / batch boundary / artifact policy 语义与兼容映射，不改既有 Canon、Raw Story Log、关系、物品、资源、时间和已经发生的选择。

对于30万字、100万字或数百回合目标，允许跨执行批次在 technical checkpoint 安全暂停与继续，但**不声称后台异步生成**。批次边界本身不等于暂停点；目标字数只计算纯小说正文，也绝不成为每回合固定字数配额。

核心目标是：
**让复杂酒馆既能由玩家长期互动，也能在明确授权后让一个受角色人格与知识约束的 Autonomous Player 真正做决定，把世界因果自然积累成几十万乃至百万字长篇；与此同时，原始故事永远可回查，长期记忆不会用摘要冒充事实。**