# ChatGPT Custom Skills

## Complex Tavern Engine v3.3

- Canonical path: `skills/complex-tavern/SKILL.md`
- Current version: `3.3.0`
- Status: `stable-default`
- Triggers: “开始复杂酒馆”, “继续复杂酒馆”, “按复杂酒馆 v3 玩”, “继续当前酒馆故事”
- Loading rule: on any Complex Tavern trigger, fetch the canonical `SKILL.md` from GitHub before starting or resuming; unless the user explicitly asks for an older version, use the latest canonical version by default.
- Source of truth: GitHub copy above. Library/local copies are backups only.
- Runtime: pure text; image generation is disabled by default.

## 不着急 / No-Rush

- Canonical path: `skills/no-rush/SKILL.md`
- Current version: `2.1.0`
- Status: `stable-default`
- Source of truth: GitHub canonical file above. Local/Library copies are fallback only.
- Loading rule: when GitHub access is available, fetch the canonical file before running No-Rush so the latest version is used.
- Activation: enabled by default. No model-name or thinking-effort check is required.
- No hard model/mode exclusions: unknown effort, Instant, Medium, High, Extra High, automatic Thinking, GPT-5.6 Sol, GPT-6 Pro, etc. do not by themselves disable No-Rush.
- Explicit disable: “这次不用不着急 / 这次关闭不着急” disables only the current task; “关闭不着急 / 暂停不着急” disables it for the current conversation until “开启不着急 / 恢复不着急”.
- Pipeline: Understanding Gate → Current Task Brief → Execution → Final Check.
- Latest-wins rule: newer explicit requirements supersede conflicting older requirements; superseded requirements must not reappear.
- Clarification convergence: normal tasks max 3 rounds; complex/contradictory tasks max 4 rounds.
- Overrides: “直接做”, “别猜”, “严格不着急”.
- Tests: `skills/no-rush/evals/evals.json`.
