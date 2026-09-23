# v4 Demo Test Plan — demo.2

This suite contains 42 contract/scenario cases. It is **not** a live host Runtime test.

Test layers:
1. Static contract anchors and forbidden contradictions.
2. Scenario rule audit against the written contract.
3. Persistence/namespace conflict audit.
4. Post-fix regression rerun.

Known unavailable live integrations in this environment:
- real vector database retrieval;
- isolated branch database with atomic multi-file transactions;
- visual Context Inspector UI;
- binary entity-card package import/export.

These must remain degraded/unavailable rather than be claimed as live-tested.
