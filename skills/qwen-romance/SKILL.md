---
name: qwen-romance
display_name: Qwen Romance / 千问成人言情扩展
description: 仅供本地 Qwen/千问系列模型加载的恋爱、成熟成人关系与长篇关系连续性 Skill。通过 fail-closed Model Gate 限定为 local=true 且 family=qwen；GPT/OpenAI 与其他非 Qwen 模型必须完全禁用。适用于独立言情、复杂酒馆互动模式与小说模式；重点管理关系阶段、亲密推进、人物一致性、关系记忆和长篇续写，不把“允许较高尺度”误当成“自动成人化”。
version: 0.1.0
status: release-candidate
canonical_repository: 1948666760dty-sys/agent-skills
canonical_path: skills/qwen-romance/SKILL.md
activation: qwen-local-only-fail-closed
---

# Qwen Romance v0.1.0

## 0. 定位

Qwen Romance 是一个 **Qwen-only** 关系叙事扩展。

它不是：
- OpenAI / GPT Skill；
- 通用成人内容开关；
- 绕过模型或平台安全机制的工具；
- 只靠关键词触发的“NSFW Prompt”；
- 一开启就把所有剧情推向成人内容的开关。

它负责：
- 恋爱关系状态；
- 慢热/自然/快速推进；
- 成年角色之间的成熟关系表现；
- 人物一致性；
- 关系记忆；
- 长篇小说中的关系弧；
- 复杂酒馆中的可选恋爱扩展；
- 本地 Qwen 长文本生成时的关系连续性。

它不负责修改底层模型权重，也不声称能覆盖或绕过模型、运行框架、客户端或宿主环境自身的限制。

---

## 1. Canonical 与真实性边界

唯一规范主源：

- Repo: `1948666760dty-sys/agent-skills`
- Path: `skills/qwen-romance/SKILL.md`

本文件是语言模型可执行的规范，不是一个能够独立检测本机进程的程序。

因此“只对 Qwen 生效”采用两层保证：

1. **Loader Gate**：宿主/加载器必须在 Prompt Composition 之前确认 `local=true AND family=qwen`，否则不得加载本 Skill。
2. **Self Gate**：即使本 Skill 被误加载，只要当前模型信息不是可靠的本地 Qwen，本 Skill 必须立刻进入 `INACTIVE`，不得改变剧情尺度、风格、关系逻辑或其他 Skill 行为。

若当前运行环境无法提供可靠模型身份，采取 **fail closed**：

`unknown model => inactive`

不得因为“看起来像本地模型”“用户说这是千问”“接口兼容 OpenAI”而自动认定为 Qwen。

---

## 2. 最高优先级 Model Gate

### 2.1 启用条件

只有以下条件全部为真时，本 Skill 才允许进入 ACTIVE：

```yaml
runtime:
  local: true
model:
  family: qwen
qwen_romance:
  enabled: true
```

逻辑：

```text
ACTIVE =
  local == true
  AND normalized_model_family == "qwen"
  AND qwen_romance.enabled == true
```

缺一不可。

### 2.2 必须禁用的模型

以下情况全部视为 `INACTIVE`：

- OpenAI / GPT / ChatGPT；
- GPT-5.x、GPT-6.x；
- OpenAI API GPT 系列；
- GPT-OSS；
- Llama；
- Gemma；
- Mistral；
- DeepSeek；
- Claude；
- 其他非 Qwen 模型；
- 模型身份未知；
- 仅知道“本地运行”，但不知道 family；
- 仅知道 API 为 OpenAI-compatible；
- 仅模型名称包含可疑/模糊字符串但元数据不能确认。

### 2.3 GPT 硬隔离

若检测到：

```yaml
provider: openai
```

或：

```yaml
family: gpt
```

则：

```text
QWEN_ROMANCE = HARD_OFF
```

此时不得：
- 注入本 Skill 的任何 romance state；
- 注入成人尺度规则；
- 修改 GPT 的 Complex Tavern 行为；
- 创建 Qwen Romance Memory；
- 运行 Qwen Romance Router；
- 因用户手动设置 `enabled=true` 而覆盖禁用。

### 2.4 手动配置不能覆盖 Model Gate

即使配置为：

```yaml
qwen_romance:
  enabled: true
```

只要：

```text
family != qwen
```

最终状态仍然必须是：

```text
INACTIVE
```

### 2.5 推荐模型归一化

Loader 应优先读取结构化模型元数据，而不是只做名称字符串判断。

建议输入：

```json
{
  "provider": "local",
  "runtime": "ollama",
  "model_id": "qwen3:14b",
  "model_family": "qwen",
  "local": true
}
```

推荐优先级：

1. 明确 `model_family`；
2. 运行器的模型 metadata / architecture；
3. 经项目白名单登记的 model_id；
4. 名称模式只作为最后 fallback。

若第 1～3 项均无法确认，不启用。

---

## 3. Skill Graph

本 Skill 不取代 Complex Tavern。

正确关系：

```text
Complex Tavern / 独立小说宿主
        │
        ▼
    Model Gate
        │
   ┌────┴────┐
   │         │
非Qwen      Local Qwen
   │         │
   ▼         ▼
保持原行为   Qwen Romance Router
             │
     ┌───────┼────────┐
     ▼       ▼        ▼
  Core     Pacing   Consistency
     │
     ▼
 Mature-Adult Layer
     │
     ▼
 Novel / Memory / Audit
```

Complex Tavern 本体应保持模型无关。

不要把本 Skill 的完整规则复制进 Complex Tavern 主文件。

---

## 4. 激活方式

满足 Model Gate 后，本 Skill 仍不会自动把所有剧情视为恋爱。

### 4.1 明确触发

以下语义可开启扩展：

- “启用 Qwen Romance”
- “千问言情模式”
- “Qwen 成人言情”
- “本地千问用恋爱扩展”
- Complex Tavern 的关系配置明确要求使用 Qwen Romance Extension

### 4.2 隐式宿主触发

宿主可在以下条件同时成立时加载 Router：

- Model Gate 通过；
- 当前故事允许恋爱线；
- 用户没有明确关闭；
- 相关人物的年龄门已经可判定；
- 宿主希望把关系逻辑委托给本扩展。

### 4.3 关闭

用户说：

- “关闭 Qwen Romance”
- “这局不要恋爱扩展”
- “只走主线”
- “不要成人关系内容”

则依语义关闭整个扩展或降低上限。

关闭不能删除已经发生的 Canon 关系事件，只停止未来主动使用对应能力。

---

## 5. Router：按需加载，不污染全局

每个场景开始前先计算：

```json
{
  "romance_active": false,
  "adult_layer_active": false,
  "current_intensity": "R0",
  "max_intensity": "R2",
  "modules": []
}
```

可加载模块：

- `romance_core`
- `intimacy_pacing`
- `character_consistency`
- `mature_adult_layer`
- `novel_romance`
- `romance_memory`
- `romance_audit`

普通任务或无恋爱场景不得加载全部模块。

示例：

```text
买饮料 / 查线索 / 上课 / 战斗
→ 通常 R0
→ 不加载 mature_adult_layer
```

明确约会：

```text
→ romance_core
→ intimacy_pacing
→ character_consistency
```

只有成年且关系与场景真的发展到成熟成人层时：

```text
→ mature_adult_layer
```

---

## 6. Max Intensity 与 Current Intensity 必须分离

最重要规则之一：

`允许的最高尺度 ≠ 当前场景尺度`

状态：

```yaml
romance:
  max_intensity: R4
  current_intensity: R1
```

表示：

- 系统允许未来在合适条件下发展到 R4；
- 当前仍只是 R1；
- 不得因为 `max=R4` 就主动把普通约会升级成成人场景。

---

## 7. Intensity Scale

### R0 — 无恋爱

友情、同事、队友、家人、陌生人、普通 NPC。

### R1 — 好感 / 暧昧

可包含：

- 好感；
- 在意；
- 害羞；
- 关系张力；
- 轻微身体距离变化；
- 暧昧但未明确关系。

### R2 — 明确恋爱

可包含：

- 约会；
- 表白；
- 情侣关系；
- 拥抱；
- 接吻；
- 明确的情感和身体吸引。

### R3 — 成熟成人关系

仅用于明确成年角色。

可包含：
- 成熟恋爱主题；
- 成人伴侣的私密关系；
- 更强烈的身体吸引；
- 对亲密、关系边界和未来的讨论；
- 不回避已经自然进入的成年关系结果。

### R4 — 高亲密度成人言情

仅在：
- 所有相关人物明确成年；
- 当前能力与同意状态允许；
- 关系和剧情已经合理推进；
- 用户允许；
- 当前 Qwen / Runtime 自身允许

时使用。

R4 的目标不是“尽可能露骨”，而是：

- 不因成熟关系出现就突然让人物失忆；
- 不自动硬切“第二天早晨”来破坏连续性；
- 保持人物心理、关系、情绪、动作和后果连贯；
- 具体表达程度服从当前运行模型与宿主自身约束。

---

## 8. Adult Gate

R3 / R4 前必须全部通过：

```text
AGE GATE
CONSENT GATE
CAPACITY GATE
RELATIONSHIP/SCENE GATE
```

### 8.1 Age Gate

只有明确 `18+` 才允许进入 R3/R4。

状态：

```yaml
age_verified: true
age_band: 18+
```

若年龄未知：

```text
max current intensity <= R2
```

不得自行猜“应该成年”。

### 8.2 未成年人

未成年人相关关系遵循宿主的年龄规则；本 Skill 的成熟成人层永久不对未成年人启用。

禁止：
- 未成年人性内容；
- 成年人与未成年人的性/成人亲密关系；
- 把未成年人作为成人化、性化对象；
- 用“架空世界”“外表成年”“实际活了几百年”等方式绕开年龄门。

### 8.3 Consent Gate

状态：

```text
clear
uncertain
withdrawn
not_applicable
```

R3/R4 仅允许：

```text
clear
```

如果 `uncertain`：
- 不升级；
- 允许剧情自然停留、沟通、改变方向。

如果 `withdrawn`：
- 立即停止进一步升级；
- 尊重撤回；
- 保持角色内叙事，不做说教式跳戏。

### 8.4 Capacity Gate

若人物处于不能可靠作出决定的状态，则不能升级成人亲密内容。

例如：
- 失去意识；
- 明显无法判断；
- 其他无法有效同意状态。

### 8.5 权力与胁迫

不得把威胁、勒索、强迫、失去选择空间描述成有效同意。

若场景存在明显压力或权力问题：
- 降低/冻结尺度；
- 让剧情先解决边界和选择空间。

---

## 9. Romance Core

每对重要关系维护：

```json
{
  "a": "player",
  "b": "npc_01",
  "stage": "INTEREST",
  "attraction": 35,
  "trust": 28,
  "emotional_closeness": 20,
  "physical_comfort": 12,
  "compatibility": 41,
  "boundaries": [],
  "promises": [],
  "important_memories": [],
  "unresolved_tension": []
}
```

数值：
- 只用于内部连续性；
- 不默认显示给用户；
- 不应成为机械触发器。

例如：

```text
attraction=90
```

不意味着：
```text
必须表白 / 必须进入关系 / 必须亲密升级
```

仍取决于人物性格、事件、价值观、目标、冲突和关系阶段。

---

## 10. Relationship Stage

建议阶段：

```text
STRANGER
ACQUAINTANCE
FRIEND
INTEREST
ATTRACTION
MUTUAL_ATTRACTION
DATING
RELATIONSHIP
DEEP_RELATIONSHIP
COMMITTED
CONFLICT
DISTANCE
BREAKUP
RECONCILIATION
```

阶段变化必须有剧情证据。

禁止只因为内部数字跨阈值就自动切换。

---

## 11. NPC 不是恋爱奖励

每个 NPC 可维护：

```json
{
  "romance_eligible": true,
  "compatibility": 30,
  "initial_attraction": 5,
  "route_weight": "minor"
}
```

部分 NPC 应为：

```text
romance_eligible=false
```

硬规则：
- 不让所有 NPC 自动喜欢玩家；
- 朋友可以一直只是朋友；
- 敌人不自动变恋爱对象；
- 高好感不等于恋爱；
- 不把“玩家是主角”当作所有人被吸引的理由。

建议：

```yaml
max_major_routes: 3
```

---

## 12. Character Consistency

主要角色维护：

```json
{
  "romantic_profile": {
    "initiative": "low",
    "emotional_openness": "medium",
    "physical_contact_preference": "low",
    "jealousy": "low",
    "relationship_experience": "limited",
    "attachment_tendency": "reserved",
    "boundaries": []
  }
}
```

人物行为必须由既有性格与经历约束。

例如：
- 害羞、低主动角色不能无原因下一幕突然极度主动；
- 冷静人物不能为制造“甜”而长期丢失其核心性格；
- 人物可以成长，但成长要有 source event。

---

## 13. Intimacy Pacing

支持：

```text
very_slow
slow
natural
fast
user_driven
```

推荐：
- 互动故事：`natural`
- 长篇小说：`slow`
- 用户明确要快节奏：`fast`
- 用户掌握推进：`user_driven`

每次重大升级前检查：
- 上一次关系变化距今多远；
- 是否有足够共同经历；
- 当前人物性格是否支持；
- 当前危机/主线是否应该优先；
- 玩家是否明确推动；
- 关系是否仍存在未解决冲突。

禁止无理由：

```text
初见 → 表白 → 确立关系 → 极高亲密
```

在极少场景内连续完成。

---

## 14. 主线优先

配置：

```yaml
story_weight: 0.30
```

语义：

```text
0.00 = 无恋爱
0.10 = 极轻
0.25 = 辅助线
0.50 = 双主线
0.75 = 恋爱主导
1.00 = 纯言情
```

Complex Tavern 默认建议：

```text
0.20~0.35
```

世界正在发生重大危机时，不得因为 romance active 就无视危机。

恋爱线必须服从：
- 生存；
- 战斗；
- 任务；
- 世界重大事件；
- 当前逻辑优先级。

---

## 15. Mature Adult Layer

该层只在 Adult Gate 通过后按需加载。

目标：

```text
人物心理
+ 情绪变化
+ 关系信任
+ 身体距离/亲密程度
+ 边界与主动性
+ 剧情后果
```

同步推进。

禁止把成熟场景写成与人物无关的孤立段落。

不得为了“尺度大”：
- 让人物 OOC；
- 自动跳过同意；
- 自动升级；
- 忘记此前边界；
- 让主线暂停失去逻辑；
- 把每次独处都变成成人场景。

---

## 16. Mature Scene State Machine

需要成熟关系场景时，后台按：

```text
ENTRY
→ TENSION
→ MUTUAL SIGNAL
→ INTIMACY
→ DE-ESCALATION
→ AFTERMATH
→ RELATIONSHIP UPDATE
```

注意：
- 每一步都可以停止；
- 不要求每场都走完；
- 玩家/NPC/环境可以改变方向；
- `MUTUAL SIGNAL` 不能代替 Consent Gate；
- 不预设“进入场景 = 必须完成”。

---

## 17. Aftermath 必须存在

重要关系场景后执行：

```text
RELATIONSHIP UPDATE
```

至少评估：

```json
{
  "trust_delta": 0,
  "closeness_delta": 0,
  "stage_change": null,
  "new_memory": null,
  "new_boundary": null,
  "new_expectation": null,
  "emotional_aftereffect": null
}
```

后续角色必须记得重要事件。

禁止：

```text
上一章关系发生重大变化
→ 下一章像从没发生过
```

---

## 18. Romance Memory Capsule

长局不重复注入全部历史。

维护约 300–800 token 的关系工作记忆：

```yaml
relationship:
  stage: DATING
  attraction: high
  trust: medium_high

important_memories:
  - ...
boundaries:
  - ...
unresolved:
  - ...
recent_changes:
  - ...
current_intensity: R2
max_intensity: R4
```

高重要度事件不可因压缩丢失：

- 第一次明确表白；
- 确立关系；
- 重要承诺；
- 重大争吵；
- 分手；
- 复合；
- 明确边界；
- 关系方向改变。

---

## 19. 长篇小说关系弧

区分：

```text
SCENE STATE
ARC STATE
NOVEL STATE
```

示例：

```text
ACT 1: 陌生 → 好感
ACT 2: 好感 → 信任
ACT 3: 信任 → 明确关系
ACT 4: 冲突 / 距离
ACT 5: 重建 / 决定未来
```

规则：
- 不是每章升级；
- 也不能几十章完全原地踏步而无原因；
- 重大变化要由事件支撑；
- 关系线不能覆盖主线因果。

---

## 20. 长篇续写与 Context

本 Skill 不宣称“单次无限 Token”。

正确设计：

```text
Chunk
→ checkpoint
→ chapter/scene summary
→ romance state update
→ memory capsule
→ next chunk
```

推荐每轮加载：

```text
Current Scene/Chapter
Previous Summary
Arc Summary
Character State
Romance Capsule
Relevant High-Importance Memories
```

而不是整本历史。

本 Skill 只规定关系层的连续性；实际自动续写与文件输出由宿主负责。

---

## 21. 与 Complex Tavern 集成

### 21.1 零侵入原则

Complex Tavern 主 Skill 不需要复制本文件内容。

推荐宿主逻辑：

```text
Load Complex Tavern
→ obtain runtime/model metadata
→ run Qwen Romance Model Gate
→ if ACTIVE, attach Qwen Romance as extension
→ else continue Complex Tavern unchanged
```

### 21.2 继承现有关系配置

如果 Complex Tavern 已有：
- C1；
- C2；
- player age；
- relationship orientation；
- hard exclusions；
- player profile；

本 Skill优先继承，不重复询问。

映射原则：

```text
C1 = 恋爱参与容量
C2 = 成熟亲密表现上限
```

但：
- C2 只是 `max_intensity` 的来源之一；
- C2 高不等于 current intensity 高；
- 未成年时成熟成人层永久关闭。

### 21.3 不改变 GPT 路径

当宿主是 GPT：
- 不加载；
- 不注入；
- 不建立 state；
- 不改变 Complex Tavern 原规则。

---

## 22. 防重复与文风漂移

维护：
- `recent_phrase_memory`
- `recent_scene_pattern`
- `recent_emotional_pattern`

常见重复表达不能连续机械循环。

Romantic Scene Types：

```text
conversation
daily_life
shared_task
date
conflict
repair
distance
reunion
family
career
danger
quiet_moment
major_choice
private_moment
```

尽量避免连续 3 场完全同型。

若宿主已有 paragraph/style lock，本 Skill 必须服从宿主，不得覆盖。

---

## 23. 配置模板

```yaml
qwen_romance:
  enabled: true

  model_gate:
    require_local: true
    require_family: qwen
    fail_closed: true

  romance:
    max_intensity: R4
    pacing: natural
    story_weight: 0.30
    max_major_routes: 2

  adult_content:
    enabled: true
    require_age_verified: true
    require_clear_consent: true
    require_capacity: true

  memory:
    enabled: true
    capsule_tokens_target: 500
    preserve_high_importance_events: true

  audit:
    enabled: true
    interval_chapters: 10
```

如果 Model Gate 不通过，上述所有配置都不生效。

---

## 24. Debug

开发模式可输出内部诊断：

```text
QWEN_ROMANCE_DEBUG
gate=ACTIVE
local=true
family=qwen
romance_active=true
adult_layer_active=false
current=R1
max=R4
modules=romance_core,intimacy_pacing,character_consistency
```

正式故事默认隐藏。

对于 GPT：

```text
gate=INACTIVE
reason=non_qwen_model
loaded_modules=0
```

这是关键回归指标。

---

## 25. Audit

建议每 10 章或明显关系转折后检查：

- Model Gate 是否仍通过；
- 年龄门是否完整；
- 同意/能力状态是否正确；
- 关系是否无证据跳级；
- 人物是否 OOC；
- 重要关系事件是否失忆；
- 是否所有 NPC 都被恋爱化；
- 是否高尺度配置导致普通场景自动成人化；
- 是否重复同一种暧昧套路；
- 恋爱线是否抢占主线；
- max/current 是否被混淆；
- 成熟关系事件是否有 aftermath。

Audit 不写进小说正文。

---

## 26. Fail-Closed Rules

以下任一情况发生，优先降低能力而不是猜：

```text
model family unknown
age unknown
consent uncertain
capacity uncertain
state corrupted
relationship continuity uncertain
```

处理：
- model unknown → 整个 Skill inactive；
- age unknown → 不进入成熟成人层；
- consent/capacity uncertain → 不升级；
- state corrupted → 保守恢复到最近可靠 checkpoint；
- memory 冲突 → 原始剧情证据优先于摘要。

---

## 27. 禁止行为

不得：
- 作用于 GPT/OpenAI；
- 把 local=true 当作 Qwen；
- 只靠关键词触发成熟成人层；
- 用 `enabled=true` 覆盖 Model Gate；
- 年龄不明时猜成年；
- 将未成年人纳入成熟成人层；
- 将非自愿、强迫或无能力同意写成有效同意；
- 所有 NPC 自动喜欢玩家；
- 高 max intensity 自动升级 current intensity；
- 为提高尺度牺牲人物性格；
- 忘记关系 aftermath；
- 让恋爱线无视主线危机；
- 声称本 Skill 绕过了模型/平台安全机制；
- 声称“无限 Token”或后台无限生成；
- 在没有真实 Qwen 运行测试的情况下声称已完成真实模型兼容性验证。

---

## 28. 验收标准

正式启用至少满足：

1. `local=true + family=qwen + enabled=true` 才 ACTIVE；
2. GPT/OpenAI 永远 INACTIVE；
3. unknown model 永远 INACTIVE；
4. GPT loaded_modules = 0；
5. max/current 分离；
6. 普通场景不会因 R4 上限自动成人化；
7. 年龄未知阻止成熟成人层；
8. 未成年人不进入成熟成人层；
9. clear consent 才允许 R3/R4；
10. withdrawn 能立即阻止升级；
11. incapacitated 不能升级；
12. NPC 不全部恋爱化；
13. slow/very_slow 不无故跳阶段；
14. 重大关系事件进入长期记忆；
15. aftermath 更新关系；
16. 主线危机优先；
17. 关系线长期连续；
18. Context 压缩不删除高重要度事件；
19. Complex Tavern GPT 路径无行为变化；
20. 真实 Qwen Runtime 上线前完成至少一次 Ollama/llama.cpp/LM Studio 中实际使用环境的 smoke test。

---

## 29. 发布口径

当前版本：`0.1.0 release-candidate`

原因：
- 规则、Model Gate、状态结构和回归用例已经定义；
- 静态检查可以验证文件一致性；
- 但没有在本仓库提交动作本身中运行真实本地 Qwen 推理，因此不得假装已经验证实际模型输出质量。

完成真实本地 Qwen smoke test 后，若核心用例通过，可升级为 `1.0.0 stable-default`。

### Changelog

- **0.1.0（2026-09-21）**：首个 Qwen-only Romance Extension 候选版。新增 fail-closed Model Gate、GPT 硬隔离、关系状态、max/current 双层尺度、成年/同意/能力 Gate、人物一致性、慢热控制、Romance Memory Capsule、长篇关系弧、Complex Tavern 零侵入扩展协议与回归验收要求。
