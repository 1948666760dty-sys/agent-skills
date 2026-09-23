# v4 Demo Test Results — demo.3

## Summary
- Original regression suite: **42 / 42 PASS**
- Extended post-fix audit suite: **50 / 50 PASS**
- Stable v3.7.1 canonical version unchanged.
- Stable v3.7.1 blob SHA unchanged: `82aaca291d676d07bdffbb7b126c2f1629a91147`.

## What was verified
- explicit Demo activation vs stable routing;
- clone-for-demo isolation;
- Single Authority and stale-proposal revision guard;
- Single Context Assembly;
- source-linked Memory provenance rules;
- Calendar/date certainty and schedule conflicts;
- Trigger eligibility-only semantics;
- Director Note expiry and non-Canon scope;
- Speaker Scheduler knowledge isolation;
- Branch fail-closed, rewind-as-new-branch and no auto-merge;
- Template/Instance no-overwrite behavior;
- player-safe Debugger/Inspector including hidden-record existence metadata;
- `/TavernSavesV4/` separation;
- versioned state snapshot + last-written commit-manifest recovery protocol.

## Not claimed as live-runtime verified
- semantic vector retrieval quality;
- real isolated branch database behavior under concurrent writes;
- actual atomic filesystem/database transactions;
- visual Context Inspector UI;
- binary entity-card package import/export.

Those capabilities remain capability-gated and must degrade/disable rather than pretend to work.
