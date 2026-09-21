# ChatGPT Custom Skills

## Complex Tavern Engine v3.5.3

- Canonical path: `skills/complex-tavern/SKILL.md`
- Current version: `3.5.3`
- Status: `stable-default`
- Triggers: “开始复杂酒馆”, “继续复杂酒馆”, “按复杂酒馆 v3 玩”, “继续当前酒馆故事”
- Loading rule: on any Complex Tavern trigger, fetch the canonical `SKILL.md` from GitHub before starting or resuming; unless the user explicitly asks for an older version, use the latest canonical version by default.
- Source of truth: GitHub copy above. Library/local copies are backups only.
- Runtime: pure text; image generation is disabled by default.

## 不着急 / No-Rush

- Canonical path: `skills/no-rush/SKILL.md`
- Current version: `2.2.0`
- Status: `stable-default`
- Source of truth: GitHub canonical file above. Local/Library copies are fallback only.
- Loading rule: when GitHub access is available, fetch the canonical file before running No-Rush so the latest version is used.
- Activation: enabled by default. No model-name or thinking-effort check is required.
- Visible confirmation: `不着急 ✓` appears before the first normal response/progress update for medium/high-complexity work, project planning, Skill edits, multi-step tasks, and understanding/feasibility assessment. Simple chat, calculation, and one-step Q&A stay silent but enabled.
- Deduplication: once per task, including progress, clarification, continuation, and final delivery; a new task resets the marker. Explicit disable suppresses it. Strict output formats take priority when there is no suitable progress message.
- Understanding gate unchanged: >=95% executes directly; <95% resolves retrievable facts first and asks only key ambiguities. The marker is confirmation of activation, not proof of understanding or completion.
- No hard model/mode exclusions: unknown effort, Instant, Medium, High, Extra High, automatic Thinking, GPT-5.6 Sol, GPT-6 Pro, etc. do not by themselves disable No-Rush.
- Explicit disable: “这次不用不着急 / 这次关闭不着急” disables only the current task; “关闭不着急 / 暂停不着急” disables it for the current conversation until “开启不着急 / 恢复不着急”.
- Pipeline: Understanding Gate → Current Task Brief → Execution → Final Check.
- Latest-wins rule: newer explicit requirements supersede conflicting older requirements; superseded requirements must not reappear.
- Clarification convergence: normal tasks max 3 rounds; complex/contradictory tasks max 4 rounds.
- Overrides: “直接做”, “别猜”, “严格不着急”.
- Tests: `skills/no-rush/evals/evals.json`.
- Marker regression: have an independent agent apply the canonical Skill to `marker_cases` and save observations; run `node skills/no-rush/evals/check-observations.cjs observations.json`. The checker validates observed activation/action labels, marker placement/count and strict JSON; key-question quality still requires reading the actual replies. Scenario definitions alone are not a passing run.
- Changelog: see the version history at the end of `skills/no-rush/SKILL.md` (v2.2.0 adds the lightweight marker; v2.1.0 removed the obsolete Extra High-only gate).


## Cut Coach / 减脂教练

- Canonical path: `skills/cut-coach/SKILL.md`
- Current version: `1.0.0`
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
