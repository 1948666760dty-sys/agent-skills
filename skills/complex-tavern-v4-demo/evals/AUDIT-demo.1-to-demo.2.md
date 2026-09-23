# Complex Tavern v4 Demo — Audit demo.1 → demo.2

## Scope
Audit of `4.0.0-demo.1` after first upload. Stable v3.7.1 was not modified.

## Findings
1. **Critical — activation ambiguity:** inherited v3 text could route ordinary “开始/继续复杂酒馆” into the demo canonical.
2. **Critical — schema collision:** inherited persistence contract still declared `state.json schema_version: 3.6.1`, risking writes that look like stable state.
3. **Major — opening mismatch:** Calendar Display Choice existed as a rule but was not part of the explicit Opening State Machine.
4. **Major — context bypass ambiguity:** Director Note Overlay appeared after Context Composer in the pipeline, undermining the single-context-entry rule.
5. **Major — trigger staleness:** `eligible` was modeled as state without saying it must be recomputed each turn.
6. **Major — stale proposal race:** Single Writer existed, but proposals had no authority revision guard.
7. **Minor — memory naming ambiguity:** memory status named `canon` could be misread as Canon ownership.
8. **Minor — weekday source:** exact dates required consistency but the authority/source of weekday calculation was underspecified.
9. **Minor — inherited regression wording:** old test #77 said “current state schema 3.6.1”, which is only true for v3.

## Fixes in demo.2
All nine findings addressed. No change to stable v3.7.1.

## Remaining high-risk areas for test phase
- branch namespace isolation;
- sibling-branch memory leakage;
- trigger consumption across branches;
- template/instance merge behavior;
- context budget eviction;
- player-safe debugger leakage.
