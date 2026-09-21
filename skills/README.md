# Skill 详细索引

[返回分类首页](../README.md) · 正式仓库：1948666760dty-sys/agent-skills

下列 canonical path 均相对于仓库根目录。

## Complex Tavern Engine v3.6.6

- Canonical path: `skills/complex-tavern/SKILL.md`
- Current version: `3.6.6`
- Status: `stable-default`
- Triggers: “开始复杂酒馆”, “继续复杂酒馆”, “按复杂酒馆 v3 玩”, “继续当前酒馆故事”
- Loading rule: on any Complex Tavern trigger, fetch the canonical `SKILL.md` from GitHub before starting or resuming; unless the user explicitly asks for an older version, use the latest canonical version by default.
- Source of truth: GitHub copy above. Library/local copies are backups only.
- Runtime: pure text; image generation is disabled by default.

## Qwen Romance / 千问成人言情扩展

- Canonical path: `skills/qwen-romance/SKILL.md`
- Current version: `0.2.0`
- Status: `release-candidate`
- Activation: **仅当 `local=true AND model_family=qwen AND enabled=true` 时允许启用；其他情况 fail closed。**
- GPT/OpenAI isolation: GPT、OpenAI、GPT-OSS、其他非 Qwen 模型与未知模型身份均必须保持 INACTIVE；GPT 路径不得注入本 Skill 正文或状态，`loaded_modules=0`。
- Scope: 恋爱关系阶段、推进节奏、人物一致性、成年角色成熟关系、关系记忆、长篇关系弧、Complex Tavern 可选扩展。
- Intensity rule: `max_intensity` 与 `current_intensity` 必须分离；允许 R4 不代表普通场景自动成人化。
- Adult gates: R3/R4 需要明确 18+、clear consent 与正常 capacity；年龄未知或状态不确定时不升级。
- Complex Tavern integration: 零侵入扩展；先加载 Complex Tavern，再由宿主 Model Gate 决定是否附加 Qwen Romance。GPT 路径保持原行为。
- Runtime contract: `skills/qwen-romance/references/runtime-contract.md`.
- Long-output contract: `skills/qwen-romance/references/long-output-contract.md`.
- Long-output behavior: adaptive `short` / `normal` / `long` / `very_long`, multi-Chunk Visible Reply, automatic continuation, dynamic token budget, seam/overlap audit, and premature-closure guard. Defaults apply only after the local-Qwen Model Gate.
- State schema: `skills/qwen-romance/references/state.schema.json`.
- Regression cases: `skills/qwen-romance/evals/evals.json`（25 个基础场景）与 `skills/qwen-romance/evals/long-output-cases.json`（15 个长输出场景），合计 40 个。
- Static checker: `python skills/qwen-romance/evals/static_check.py`.
- Release note: 当前为 0.2.0 RC；规则与静态检查已建立，但在真实本地 Qwen Runtime 完成 smoke test 前不得声称已经验证实际模型兼容性。

## 不着急 / No-Rush

- Canonical path: `skills/no-rush/SKILL.md`
- Current version: `2.4.0`
- Status: `stable-default`
- Source of truth: GitHub canonical file above. Local/Library copies are fallback only.
- Loading rule: when GitHub access is available, fetch the canonical file before running No-Rush so the latest version is used.
- Activation: enabled by default. No model-name or thinking-effort check is required.
- Visible confirmation: every user turn must expose No-Rush status before the first visible assistant content. Enabled = `不着急 ✓`; explicitly disabled = `不着急 ✗`. Complexity no longer controls visibility, so simple chat, calculation, one-step Q&A, continuations, and short acknowledgements are also marked.
- Deduplication: exactly once per user turn, not once per task. A new user message always resets status display, even for the same task. Multiple assistant messages in the same turn share one marker. Strict JSON/code/template delivery gets a separate visible status message first so the payload itself can remain strict.
- Understanding gate unchanged: >=95% executes directly; <95% resolves retrievable facts first and asks only key ambiguities. The marker is confirmation of activation, not proof of understanding or completion.
- No hard model/mode exclusions: unknown effort, Instant, Medium, High, Extra High, automatic Thinking, GPT-5.6 Sol, GPT-6 Pro, etc. do not by themselves disable No-Rush.
- Explicit disable: “这次不用不着急 / 这次关闭不着急” disables only the current task; “关闭不着急 / 暂停不着急” disables it for the current conversation until “开启不着急 / 恢复不着急”.
- Pipeline: Understanding Gate → Current Task Brief → Execution → Final Check → Closing Status Report.
- Closing status: on every delivery, staged delivery, or execution pause while No-Rush is enabled, end with four visible fields in this order: 已完成 / 未完成 / 存在问题 / 需要你确认. Empty fields must say 无. Only genuine user decisions belong in 需要你确认.
- Latest-wins rule: newer explicit requirements supersede conflicting older requirements; superseded requirements must not reappear.
- Clarification convergence: normal tasks max 3 rounds; complex/contradictory tasks max 4 rounds.
- Overrides: “直接做”, “别猜”, “严格不着急”.
- Tests: `skills/no-rush/evals/evals.json`.
- Marker regression: have an independent agent apply the canonical Skill to `marker_cases` and save observations; run `node skills/no-rush/evals/check-observations.cjs observations.json`. The checker validates observed activation/action labels, marker placement/count and strict JSON; key-question quality still requires reading the actual replies. Scenario definitions alone are not a passing run.
- Changelog: see the version history at the end of `skills/no-rush/SKILL.md` (v2.4.0 adds the mandatory four-field closing status report; v2.3.0 makes status visible on 100% of user turns; v2.2.0 introduced the earlier complexity-based marker; v2.1.0 removed the obsolete Extra High-only gate).


## Cut Coach / 减脂教练

- Canonical path: `skills/cut-coach/SKILL.md`
- Current version: `1.1.0`
- Status: `stable-default`
- Activation: semantic auto-trigger.
- Strong triggers: food/meal/drink/nutrition-label photos related to the user's own intake; “我吃了…”, “我喝了…”, “刚吃…”, “今天吃了…”, “这个我全吃了”, “剩了这么多”, “今天还能吃多少”, “日报”, “周报”, “月报”, “Cut Coach”, “减脂教练”, “duty-NAV”.
- Query-only mode: generic nutrition questions without an indication that the user consumed the food are analyzed but are not written into the daily ledger.
- Personal targets: 2100 kcal, protein 120 g, carbs 220 g, fat 60 g, fiber 30 g.
- Percentages: duty-NAV only by default; official NRV is disabled unless the user explicitly re-enables it.
- Core loop: identify consumed food → estimate portion and uncertainty → calculate nutrition → duty-NAV → daily ledger → day-stage detection → next-meal/next-step coaching → daily/weekly/monthly reports.
- Exercise: log exercise when supplied, but do not automatically eat back or subtract exercise calories from the duty-NAV target.
- Daily ledger safety: missing meals/records must not be treated as zero intake; incomplete days are marked INCOMPLETE.
- Weekly report: formal 7-day trend requires at least 4 FULL/ESTIMATED days; otherwise generate a data-insufficient snapshot.
- Style: concise, direct, no default emoji, no food shaming.
- Loading rule: when GitHub access is available, fetch the canonical file on trigger and use it over older chat memory or fallback copies.
- Source of truth: GitHub canonical file above.
