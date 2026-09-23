# v4 Demo Test Results — demo.2

## Result
- Contract/scenario cases: **36 / 42 PASS**
- Failures: 6
- Live vector/branch database runtime: not available, therefore not claimed.

## Failed cases
- V4-002 — Demo banner was not explicitly labeled “GitHub Demo canonical”.
- V4-004 — Demo save discovery still shared the stable `/TavernSaves/` namespace.
- V4-011 — player-safe Context Inspector hid content but did not explicitly hide private-record existence metadata.
- V4-036 — player-safe Debugger had the same existence-metadata leak risk.
- V4-038 — multi-file persistence lacked a commit_id/commit-manifest transaction marker.
- V4-039 — stable and Demo saves were not rooted in separate namespaces.

## Extra audit findings
- One migration sentence still initialized schema_version=4.0-demo.1.
- runtime-state.json duplicated authority state already represented by the main state snapshot.
- Version banner wording could be mistaken for stable canonical verification.

These findings are fixed in demo.3 and must be rerun.
