# Skill 详细索引

[返回分类首页](../README.md) · 正式仓库：1948666760dty-sys/agent-skills

下列 canonical path 均相对于仓库根目录。

## Complex Tavern Engine v3.7.1

- Canonical path: `skills/complex-tavern/SKILL.md`
- Current version: `3.7.1`
- Status: `stable-default`
- Triggers: “开始复杂酒馆”, “继续复杂酒馆”, “按复杂酒馆 v3 玩”, “继续当前酒馆故事”
- Loading rule: on any Complex Tavern trigger, fetch the canonical `SKILL.md` from GitHub before starting or resuming; unless the user explicitly asks for an older version, use the latest canonical version by default.
- Source of truth: GitHub copy above. Library/local copies are backups only.
- Runtime: pure text; image generation is disabled by default.
- v3.7.1 cast-identity hotfix: recurring unnamed characters now keep stable entity IDs and role slots; later names require an explicit in-story/user/Canon source and bind to the same entity. Adds no-convenience-naming, cross-story isolation, role-collision protection, Entity Resolution Pass, cast-identity Preflight/Deep Audit, and regression cases 230–243. v3.7.0 relationship-stage behavior remains intact.


## Complex Tavern Engine v4 Demo

- Demo path: `skills/complex-tavern-v4-demo/SKILL.md`
- Current demo version: `4.0.0-demo.4`
- Status: `experimental-demo`
- Activation: explicit only — “复杂酒馆 4.0 demo / v4 demo / 继续 4.0 demo”. Ordinary Complex Tavern triggers still use stable v3.7.1.
- Safety architecture: Single Authority, Single Context Assembly, branch scoping, capability registry, fail-closed high-risk modules.
- Included demo modules: Calendar & Day Rhythm; Context Composer/Inspector; Source-linked Memory; Director Note; Trigger Eligibility; Branch/Checkpoint contract; Group Speaker Scheduler; Entity Template/Instance; read-only Continuity Debugger.
- Save isolation: `/TavernSavesV4/`; v3 saves are clone-for-demo/read-only and never overwritten in place.
- Regression: **80/80 rule-level/static logic checks passed on demo.4**. Real vector DB / isolated branch database / visual inspector / transactional backend / binary card package integrations remain unverified runtime capabilities and must stay degraded/unavailable until a host provides them.

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
- Current version: `1.5.1`
- Status: `stable-default`
- Activation: semantic auto-trigger.
- Naming: `duty-NRV`, `Cut Coach`, `减脂教练` are the same Skill and share one ledger/ruleset; `duty-NAV` remains only a historical compatibility alias.
- Personal targets: 2100 kcal; protein = latest confirmed bodyweight × 2.0 g (currently 68 kg → 136 g); carbs 220 g; fat 60 g; fiber 30 g.
- Percentages: user-visible percentages default to personal NRV only; official/China food-label NRV appears only when explicitly requested.
- Daily output: current-day 5-item personal-NRV progress bars + grouped confirmed consumed item names by meal + next action.
- Daily scoring v1.5.0: A-plan “减脂优先” total score = **execution 80% + food quality 20%**.
- Score copy v1.5.1: every score must include an overall interpretation, strengths, main deductions, and one highest-value action for tomorrow; unknown nutrient fields are never invented.
- Execution score weights: calories 30 / protein 30 / fiber 15 / fat 15 / carbs 10. Calories use a two-sided target band so extreme under-eating is penalized rather than rewarded.
- Food-quality score: fruit/vegetable coverage, minimally processed ratio, fiber, added sugar, saturated fat, sodium, and protein-source diversity. Missing fields are excluded and renormalized, never silently scored as zero.
- Score safety: INCOMPLETE days cannot receive a final daily score; midday scores are provisional; score confidence and record completeness are shown; exercise kcal does not directly add score or erase intake.
- Default strategy: A3+B1 = strong proactive coaching + low logging burden.
- Data quality: A–E estimation confidence, FULL/ESTIMATED/INCOMPLETE coverage, range-first handling of photo estimates, and no fake precision.
- Loading rule: when GitHub access is available, fetch the canonical file on trigger and use it over older chat memory or fallback copies.
- Regression: `skills/cut-coach/REGRESSION-AUDIT-v1.5.0.md`.
- Source of truth: GitHub canonical file above.
