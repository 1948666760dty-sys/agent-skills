# Complex Tavern v4 Demo — demo.4 Final Logic Audit

## Conflicts resolved in demo.4
1. **Schema conflict** — clone initialization, state contract and run summary now use `4.0-demo.4` for the current Demo schema. Historical v3 schema references remain history only.
2. **Activation conflict** — ordinary Complex Tavern triggers remain stable; explicit v4 triggers start Demo; bare `继续` inside an already bound v4 story continues the active story/version.
3. **First-visible-line conflict** — No-Rush and Demo version confirmation use one combined first line.
4. **Dual-pipeline conflict** — v4 Safe Pipeline is the single macro flow; inherited v3 1–19 entries are responsibilities/mappings only and cannot execute Context/Delta/Persistence twice.
5. **Branch-scope conflict** — write scope is current branch; read scope may include ancestor history only up to the fork turn.
6. **Trigger/time conflict** — deterministic deadlines/appointments are calendar facts; optional Trigger eligibility cannot erase them.
7. **Telemetry truthfulness** — Context Inspector may only claim loaded/excluded/token data from an actual trace; otherwise it must label output conceptual.
8. **Calendar rendering ambiguity** — last-visible date/scene state governs daily header de-duplication and restore behavior.
9. **Director-note counting ambiguity** — `turns=N` counts committed narrative turns, not meta queries/audits/failed drafts.
10. **Imported-content control risk** — cards/lore/logs are untrusted story data, not runtime instructions.

## Additional player-facing fixes
- user-confirmed 20-item interaction profile;
- author-layer naming does not generate self-aware NPC dialogue;
- anti-repair-signposting guard prevents mechanical 'no hug/no sweetness' prose;
- technical/task phase closure guard prevents endless issue-discovery loops.

## Remaining limitations
The Skill contract is internally cleaner after demo.4, but external Runtime implementations can still introduce bugs. Especially branch storage, vector retrieval and transactional persistence need separate real-system tests when those backends exist.
