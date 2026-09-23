# Complex Tavern v4 Demo — Final Audit (demo.3)

## Verdict
`4.0.0-demo.3` passes the current rule-level and scenario-level Demo gate: **50/50**.

## Risk posture
- Low-risk modules enabled by contract: Calendar, logical Context Composer, Director Note, Speaker Scheduler, read-only Debugger.
- Medium-risk modules constrained: Trigger = eligibility-only; Memory = source-linked fallback unless true retriever verified; Entity Card = Template/Instance no-overwrite.
- High-risk module default-off: Branch Manager until isolated persistent namespace is verified.

## Core invariants
1. One authority owns each state domain.
2. Only Context Composer assembles story context.
3. Memory/Trigger/Debugger/Templates never directly write Canon.
4. Branch-scoped state never leaks across siblings.
5. Demo saves live under `/TavernSavesV4/`; stable saves are untouched.
6. Multi-file commits use immutable/versioned artifacts and a last-written commit manifest.
7. Missing runtime capability fails closed or degrades truthfully.

## Remaining limitation
This is still a Skill/runtime contract demo, not a fully implemented external runtime. Passing this audit means the written arbitration, safety boundaries and regression expectations are internally consistent; it does not prove a future vector database or branch storage backend implementation is bug-free.
