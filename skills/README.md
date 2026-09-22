# Skill 详细索引

[返回分类首页](../README.md) · 正式仓库：1948666760dty-sys/agent-skills

下列 canonical path 均相对于仓库根目录。

## Complex Tavern Engine v3.6.7

- Canonical path: `skills/complex-tavern/SKILL.md`
- Current version: `3.6.7`
- Status: `stable-default`
- Triggers: “开始复杂酒馆”, “继续复杂酒馆”, “按复杂酒馆 v3 玩”, “继续当前酒馆故事”
- Loading rule: on any Complex Tavern trigger, fetch the canonical `SKILL.md` from GitHub before starting or resuming; unless the user explicitly asks for an older version, use the latest canonical version by default.
- Source of truth: GitHub copy above. Library/local copies are backups only.
- Runtime: pure text; image generation is disabled by default.


## Video Understanding / 视频理解

- Canonical path: `skills/video-understanding/SKILL.md`
- Current version: `0.2.3`
- Status: `release-candidate`
- Activation: current-chat video attachment or supported Bilibili/YouTube URL.
- Core direction: **Upload-First + Long-Video Agentic Understanding**.
- Inputs: video attachment when the host can access/materialize it; Bilibili/B站; YouTube.
- Long-video tiers: short / standard / long / very_long / ultra_long. 1–3 hour videos use chaptered retrieval and bounded evidence windows instead of one-shot full-context loading.
- Quality-first runtime policy: no default speed target; a 60-minute video may take about 60–120 minutes or longer when deeper ASR, denser visual coverage, more rewatch, or better verification improves reliability.
- Mobile-Native quality: a video uploaded from mobile is not automatically downgraded; when the host can keep executing, mobile deep analysis may use the same long processing budget as desktop. This does not imply guaranteed background execution after leaving the chat.
- Runtime: `skills/video-understanding/runtime/`.
- Runtime v0.2.3: faster-whisper >=1.2.1, PySceneDetect, FFprobe/FFmpeg Media Health, Audio tri-state, Completion Guard, corrupt-video partial fallback/repair, adaptive overview frames, Evidence Memory, dense rewatch, MCP ImageContent.
- Completion Guard: Deep visual coverage <98% or missing required speech/caption coverage => PARTIAL; audio-present / decodable / transcribed are reported separately.
- Identity Guard: task_id + request_fingerprint + session/source fingerprint prevent stale-result cross-talk.
- MCP tools: URL start, uploaded-file start, wait, manifest, transcript, chapters, search memory, inspect frames.
- Upload security: MCP local-file reads are restricted to `~/.video-understanding/inbox` or explicit `VIDEO_UPLOAD_ROOTS`; arbitrary local path access is rejected.
- Runtime contract: `skills/video-understanding/references/runtime-contract.md`.
- Regression cases: `skills/video-understanding/evals/evals.json` (50 cases).
- v0.2.3 audit: `skills/video-understanding/evals/RESULTS-v0.2.3.md` — real healthy/corrupt MP4 regression passed; repair truncation guard passed; GitHub Actions runs 35668142940 and 35668408072 passed; the second run additionally completed real faster-whisper 1.2.1 tiny-model speech inference.
- Stable gate: real short upload + 30–90m + 90–180m tests, Bilibili/YouTube, ASR fallback, scene success/fallback, memory retrieval, rewatch and upload-path security.

## 不着急 / No-Rush

- Canonical path: `skills/no-rush/SKILL.md`
- Current version: `2.5.0`
- Status: `stable-default`
- Source of truth: GitHub canonical file above. Local/Library copies are fallback only.
- **Activation contract: default-preload / zero-keyword.** The user does not need to mention “不着急”, “No-Rush”, a model name, or a thinking mode. Any host integrating this repository should load No-Rush in its preflight/default controller chain before handling the first user turn.
- Host limitation: a `SKILL.md` cannot execute before the host loads it. If a client discovers Skills only after matching a user keyword, true always-on behavior is impossible until the host/router is configured to preload No-Rush. Do not claim repo upload alone fixes that runtime layer.
- Host integration guide: `skills/no-rush/HOST-INTEGRATION.md`.
- Loading rule: when GitHub access is available, fetch the canonical file before running No-Rush so the latest version is used.
- Visible confirmation: every user turn must expose No-Rush status before the first visible assistant content. Enabled = `不着急 ✓`; explicitly disabled = `不着急 ✗`.
- Question Scan: complex/design/project/Skill-workflow tasks scan GOAL / SCOPE / USER PREFERENCE / ROUTE / DELIVERABLE / ACCEPTANCE before execution.
- Clarification levels: Q1 blocking choices must be asked unless delegated/direct-do; Q2 high-value optimization questions should normally be asked on complex tasks (1–2); Q3 low-value details should not block execution.
- Ownership rule: “the model can choose a reasonable default” is not enough to bypass a material user preference or route choice. Search/retrieval replaces factual questions, not user-owned decisions.
- Understanding gate: >=95% executes when no unresolved Q1/Q2 remains; <95% resolves retrievable facts first, then asks only material ambiguities.
- Explicit delegation: “你决定 / 都可以 / 你看着办 / 剩下你定” converts the relevant choice to DELEGATED and prevents re-asking.
- Explicit fast path: “直接做” skips Stage A questions for that task but still keeps Task Brief and Final Check.
- No hard model/mode exclusions: unknown effort, Instant, Medium, High, Extra High, automatic Thinking, GPT-5.6 Sol, GPT-6 Pro, etc. do not by themselves disable No-Rush.
- Explicit disable: “这次不用不着急 / 这次关闭不着急” disables only the current task; “关闭不着急 / 暂停不着急” disables it for the current conversation until “开启不着急 / 恢复不着急”.
- Pipeline: Host Preload → Status → Question Scan / Understanding Gate → Current Task Brief → Execution → Final Check → Closing Status Report.
- Closing status: on every delivery, staged delivery, or execution pause while No-Rush is enabled, end with four visible fields in this order: 已完成 / 未完成 / 存在问题 / 需要你确认. Empty fields must say 无.
- Latest-wins rule: newer explicit requirements supersede conflicting older requirements; superseded requirements must not reappear.
- Clarification convergence: normal tasks max 3 rounds; complex/contradictory tasks max 4 rounds.
- Tests: `skills/no-rush/evals/evals.json`.
- v2.5.0 audit: `skills/no-rush/evals/RESULTS-v2.5.0.md` — 28/28 static checks passed; 100 regression scenarios defined. Independent live host/model observations remain a separate runtime test.
- Marker regression: have an independent agent apply the canonical Skill to `marker_cases` and save observations; run `node skills/no-rush/evals/check-observations.cjs observations.json`. Static/contract audit does not substitute for a live host/model run.
- Changelog: see `skills/no-rush/SKILL.md`; v2.5.0 adds Question Scan and the zero-keyword host preload contract.

## duty-NRV / Cut Coach / 减脂教练

- Canonical path: `skills/cut-coach/SKILL.md`
- Current version: `1.3.0`
- Status: `stable-default`
- Activation: semantic auto-trigger.
- Naming: `duty-NRV`, `Cut Coach`, `减脂教练` are the same Skill and share one ledger/ruleset; `cut-coach` is only the repository path. `duty-NAV` is an internal personal-target metric.
- Strong triggers: food/meal/drink/nutrition-label photos related to the user's own intake; “我吃了…”, “我喝了…”, “刚吃…”, “今天吃了…”, “这个我全吃了”, “剩了这么多”, “今天还能吃多少”, “日报”, “周报”, “月报”, “duty-NRV”, “Cut Coach”, “减脂教练”, “duty-NAV”.
- Query-only mode: generic nutrition questions without an indication that the user consumed the food are analyzed but are not written into the daily ledger.
- Personal targets: 2100 kcal, protein 120 g, carbs 220 g, fat 60 g, fiber 30 g.
- Percentages: duty-NAV only by default; official NRV is disabled unless the user explicitly re-enables it.
- Default strategy: A3+B1 = strong proactive coaching + low logging burden.
- Core loop: identify planned/served/consumed/corrected state → estimate range + A–E confidence → duty-NAV → daily ledger → day-stage + intervention level → next action → 7/14-day trend audit and reports.
- Exercise: log exercise when supplied; wearable kcal is reference-only and is not automatically eaten back or subtracted from the duty-NAV target.
- Daily ledger safety: missing meals/records must not be treated as zero intake; incomplete days are marked INCOMPLETE.
- Weekly report: formal 7-day trend requires at least 4 FULL/ESTIMATED days; otherwise generate a data-insufficient snapshot.
- Style: concise, direct, no default emoji, no food shaming; NORMAL/NOTICE/INTERVENE proactive coaching, with only one main behavior focus per day.
- Loading rule: when GitHub access is available, fetch the canonical file on trigger and use it over older chat memory or fallback copies.
- Source of truth: GitHub canonical file above.
