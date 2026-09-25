# 2026-09-25 scoped demo.6 audit

Source baseline: `9e7db25c4764a74de9643ccc952a7d360ba81a22`.
Stable: v3.7.1. Demo: v4.0.0-demo.6, schema 4.0-demo.4.

## Release decision

NOT READY FOR STABLE. This is a report-only commit on an isolated audit branch. It does not modify SKILL.md, install a Chat runtime, deploy the candidate, change stable/no-rush, or modify any story save.

## Scope and evidence

GitHub connector reads covered repository metadata, the fixed source revision, README, relevant checker functions and key specification sections. The entire source tree was not obtained in the local runtime and this was not a complete line-by-line repository audit.

Related functions and the original 40 checks were transcribed into a clearly labeled source excerpt and executed locally. This is not a claim that the complete upstream script or historical 80-case suite ran. The complete local candidate, original observations, three candidate snapshots, test fixtures and reports are delivered separately in the audit artifact from this conversation.

Actual local results:
- Original 40 function-level checks replayed: 40/40.
- Independent 62 fixtures on original excerpt: 38/62. There are 24 failing fixture instances, not 24 distinct bugs or a measured user failure rate.
- Same 62 fixtures on final local candidate audit-r3: 62/62.
- Original 37 output-structure fixtures on candidate: 37/37. The original three text-only-helper tests are not evidence for context binding.
- New context-bound receipt checks: 41/41.
- Deliberate candidate mutations detected: 8/8.
- Synthetic sequences, five genre labels times lengths 30/50/100: 900 valid outputs accepted, 900 corrupted variants rejected, 885 stale receipts rejected. These are NOT LLM gameplay turns and NOT five tested game openings.
- Real ordinary Chat, mobile, Work gameplay, LLM long sessions and actual branch/transaction backend tests: 0, NOT VERIFIED.

## Findings

1. Single/list/noncanonical letter references can name unavailable options without rejection.
2. Stripping indentation and simplistic fence/comment handling can count code or hidden examples as active menus; dropping visible blocks can also hide invalid footer placement.
3. Broad startswith filtering drops legitimate narrative beginning with the skill name or no-rush wording.
4. Boolean annotations do not reject truthy strings such as "false" at the checker boundary.
5. same_validated_output only proves text identity. Using it as a state/authorization delivery receipt would be unsafe; this is an applicability risk, not a claim that its documented text-only comparison is incorrectly implemented.
6. A negated sentence containing the free-action keyword can satisfy the old free-action test.
7. Invalid Unicode can raise instead of returning a controlled failure; the candidate adds a conservative input contract for invisible controls.

Six checker/input-robustness issue groups and one receipt applicability risk were recorded. Local candidate repairs are not deployed upstream.

## Architecture risks requiring verification

Section 2.2 needs an explicit invalidation/recheck rule if authority validation changes or rejects state after final-text preflight. Section 18.1's manifest protocol still needs real backend tests for parent linkage, content integrity, concurrency, idempotency and delivery failure. These are design risks, not reproduced live story corruption.

## Next gates

Obtain and verify the full source bytes; integrate the candidate into an actual authorized host; collect real per-turn input/output/state evidence; execute five full openings and 30/50/100-decision trajectories; test cold resume and backend faults; compare stable and Demo under identical conditions. Until then, retain experimental status and all unavailable-capability boundaries.
