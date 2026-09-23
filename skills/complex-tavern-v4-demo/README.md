# Complex Tavern v4 Demo

- Version: `4.0.0-demo.4`
- Status: `experimental-demo`
- Stable remains: `skills/complex-tavern/SKILL.md`
- Demo path: `skills/complex-tavern-v4-demo/SKILL.md`
- Activation: explicit only — “复杂酒馆 4.0 demo”.
- Safety: Single Authority, Single Context Assembly, branch scoping, fail-closed high-risk modules.
- Included contracts: Calendar & Day Rhythm; Context Composer/Inspector; Source-linked Memory; Director Note; Trigger Eligibility; Branch/Checkpoint; Group Speaker Scheduler; Entity Template/Instance; read-only Continuity Debugger.
- Runtime truthfulness: vector RAG, isolated branch persistence, package export and visual inspector are only active when the host really provides them.
- v3 saves are never overwritten in place; use clone_for_demo semantics.

## demo.2 audit fixes
- Demo activation no longer intercepts ordinary stable triggers.
- Demo state schema is isolated from v3.
- Calendar choice is part of the Opening State Machine.
- Director Notes route through Context Composer instead of bypassing it.
- Trigger eligibility is derived per turn; stale eligibility is not persisted.
- Authority revisions reject stale proposals.

## demo.3 test-audit fixes
- Separate `/TavernSavesV4/` namespace from stable saves.
- Demo-specific visible version banner.
- Player-safe Inspector/Debugger hide private-record existence metadata as well as content.
- Versioned branch state snapshots + `commit_id` + last-written commit manifest prevent torn multi-file state.
- Removed duplicated runtime/calendar/trigger authority files.
- `with_history` exports still exclude NPC Private State unless explicit GM/Audit export is authorized.

## demo.4
- Locks the user's 20 interaction preferences.
- Resolves No-Rush/version first-line contention with a combined banner.
- Unifies current Demo schema at `4.0-demo.4`.
- Clarifies stable-vs-demo continuation routing.
- Makes v4 Safe Pipeline the only macro execution flow; inherited v3 stages are responsibilities only.
- Separates branch write scope from legal ancestor read scope.
- Separates deterministic calendar obligations from optional Trigger candidates.
- Adds truthful Context telemetry rules, Day Header display state, author/diegesis firewall, task-closure and anti-repair-signposting guards.
