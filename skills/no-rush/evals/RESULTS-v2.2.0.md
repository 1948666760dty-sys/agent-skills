# No-Rush v2.2.0 targeted regression — 2026-09-21

## Method and scope

An independent agent read the exact Skill and generated simulated replies from scenario inputs, without the expected-answer contracts. The new-version run used only each scenario's name, context, and request. The evaluator performed no external task actions and did not fetch a different canonical version. Mode names were scenario context: this was **not** a live test across eight distinct model deployments or a ChatGPT Library installation test.

## Baseline (v2.1.0, repository base 4297bc065d1d7458b26cf7d7b8939db70158af30)

Before editing the Skill, a separate evaluator simulated six scenarios. All replies lacked the marker. The three complex scenarios therefore failed the new visible-confirmation requirement:

| Scenario | Observed opening | New marker requirement |
| --- | --- | --- |
| Instant project planning | 我会按离线使用、账单导入、交易分类和统计四部分整理方案 | FAIL: absent |
| Unknown mode Skill modification | 建议保留“理解门槛 → 需求定稿 → 执行 → 交卷前检查” | FAIL: absent |
| Extra High unclear project / feasibility | 我目前没有昨天项目的具体信息，无法可靠判断重做是否可行 | FAIL: absent |

The other baseline scenarios were simple calculation, greeting, and explicit current-task disable; none displayed a marker, as desired.

## v2.2.0 result

- **21/21 new marker scenarios passed** the observation checker. Actual generated replies are in `observations-v2.2.0.json`.
- Eight mode contexts: Instant, Medium, High, Extra High, GPT-6 Pro, unknown, GPT-5.6 Sol, automatic Thinking. Each kept activation enabled, showed one opening marker, and omitted it from the final message after progress.
- Simple chat, calculation, and one-step translation remained enabled without a marker.
- Skill modification, exactly-95% understanding, and below-95% understanding behaved as specified. Reading the actual replies confirmed direct execution at the boundary and only key clarification below it, without inventing a project plan.
- Current-task disable, conversation disable, restore, and the next task after temporary disable passed.
- Same-task continuation omitted a repeated marker; a new complex task showed it again.
- Strict JSON output remained parseable, with no inserted marker.
- Checker negative control: injected a missing marker, duplicate marker, wrong disabled state, and wrong gate action. All four were rejected (exit 1).
- Versions agree across the Skill, registry README, and eval definitions. All 16 legacy scenario inputs and existing expectations were preserved; they were **not all re-executed** in this targeted run. Total definitions: 16 legacy + 21 marker scenarios.
- Repository search found no active Extra High-only activation rule. Remaining references explicitly reject the old gate or document its removal. No corresponding manifest existed.

Replay the recorded observations:

```sh
node skills/no-rush/evals/check-observations.cjs skills/no-rush/evals/observations-v2.2.0.json
```

This command checks the saved behavioral sample, not a fresh model execution. For a fresh evaluation, independently apply the Skill to the scenario inputs and pass the newly generated observations to the same checker. The enabled/action fields are evaluator annotations; marker placement/count and JSON formatting are checked directly from reply text. These results do not establish a guaranteed trigger rate in future conversations.
