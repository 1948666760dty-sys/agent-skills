# Qwen Romance Long Output Contract v0.2.0

本文件是给本地 Qwen 宿主 Runtime 的接入契约。它定义一次用户可见回复（Visible Reply）如何由多个内部模型 Chunk 组成；它不是一个可以独立调用模型的 Python Runtime。宿主必须先通过 `runtime-contract.md` 的 Model Gate，只有 `local=true` 且 `model_family=qwen` 时才能加载它。

## 1. 数据结构

```python
from dataclasses import dataclass, field
from typing import Literal

LengthMode = Literal["short", "normal", "long", "very_long"]

@dataclass(frozen=True)
class OutputProfile:
    mode: LengthMode
    soft_min_chars: int
    preferred_chars: int
    hard_target_ceiling_chars: int

@dataclass(frozen=True)
class TokenBudget:
    context_window: int
    prompt_tokens: int
    reserved_tokens: int
    available_generation_tokens: int
    runtime_parameter: str  # num_predict / n_predict / max_tokens, after adapter discovery

@dataclass
class ChunkDraft:
    text: str
    finish_reason: str
    scene_state: dict
    temporary_relationship_delta: list[dict] = field(default_factory=list)
    style_signature: dict = field(default_factory=dict)

@dataclass(frozen=True)
class ContinuationDecision:
    continue_generation: bool
    reason: str
    scene_completion: str  # natural / decision_gate / paused / ceiling / technical_boundary

@dataclass
class VisibleReply:
    text: str
    chunks: list[ChunkDraft]
    mode: LengthMode
    character_count: int
    committed_event_ids: list[str]
```

## 2. Profiles

These defaults are configurable and are measured in Chinese characters. They are guidance rather than a reason to add filler:

```python
PROFILES = {
    "short":      {"soft_min_chars": 0,    "preferred_chars": 800,  "hard_target_ceiling_chars": 1600},
    "normal":     {"soft_min_chars": 600,  "preferred_chars": 1600, "hard_target_ceiling_chars": 3000},
    "long":       {"soft_min_chars": 2500, "preferred_chars": 4000, "hard_target_ceiling_chars": 6500},
    "very_long":  {"soft_min_chars": 7000, "preferred_chars": 10000,"hard_target_ceiling_chars": 16000},
}
```

The interactive default is `long`; autonomous novel mode defaults to `very_long` with a separate soft minimum of 5000, preferred length of 8000, and ceiling of 12000. A natural short scene may stop below a soft minimum. The controller must never count audit text, summaries, state JSON, or internal reasoning as story characters.

## 3. Dynamic budget

The runtime must count the actual prompt with its tokenizer before every Chunk. A safe implementation is:

```python
def make_budget(context_window, prompt_tokens, requested_tokens, reserve_ratio=0.15,
                min_reserve=256, runtime_parameter="discovered"):
    reserve = max(min_reserve, int(context_window * reserve_ratio))
    available = context_window - prompt_tokens - reserve
    if available <= 0:
        raise ContextCapacityError("当前上下文没有足够的生成预算")
    return TokenBudget(
        context_window=context_window,
        prompt_tokens=prompt_tokens,
        reserved_tokens=reserve,
        available_generation_tokens=min(requested_tokens, available),
        runtime_parameter=runtime_parameter,
    )
```

Before reducing the profile, compress only low-importance Working Context. Preserve Canon, major relationship events, core character state, Hard Exclusions, Age Gate, Romance State, and open foreshadowing. The adapter must discover the field accepted by the actual runtime: Ollama may expose `num_predict`, llama.cpp may expose `n_predict`, and an OpenAI-compatible local server may expose `max_tokens`. These names are examples, not a hard-coded assumption.

## 4. Chunk loop

```python
def generate_visible_reply(task, mode, host, signal):
    assert host.local is True and host.model_family == "qwen"
    profile = resolve_profile(task, mode)  # /length and “写长一点” are task-scoped
    chunks = []
    temporary_events = []

    for index in range(4):  # configurable max_internal_chunks; default 4
        prompt = compose_prompt(
            task=task,
            recent_chunks=chunks[-1:],
            scene_state=task.scene_state,
            relationship_state=task.relationship_state,
            open_actions=task.open_actions,
            narrative_layout_profile=task.style_signature,
            continuation=index > 0,
        )
        budget = make_budget(host.context_window, host.count_tokens(prompt),
                             profile.preferred_chars_to_tokens)
        chunk = host.generate(prompt, budget, signal=signal)
        validate_finish_reason(chunk.finish_reason)
        chunks.append(chunk)
        temporary_events.extend(chunk.temporary_relationship_delta)

        decision = decide_continuation(chunks, profile, task)
        if not decision.continue_generation:
            break

    merged = seam_audit_and_merge(chunks, profile)
    committed_ids = commit_relationship_events_once(temporary_events)
    return VisibleReply(merged.text, chunks, profile.mode,
                        count_story_chars(merged.text), committed_ids)
```

On continuation, the prompt must contain `CONTINUE DIRECTLY FROM PREVIOUS TEXT`, the last one to three paragraphs, current physical/emotional state, POV, tense, relationship state, open actions, and the same `narrative_layout_profile`. It must explicitly prohibit summarizing, restarting, repeating, or adding a heading unless structurally required. A Chunk ending because its API budget was exhausted is a technical boundary, not a story ending.

## 5. Stop and closure rules

`decide_continuation` may stop only when a scene is naturally complete, reaches an explicit Decision Gate, the user pauses, a natural chapter point is reached, or the visible-reply ceiling is a reasonable limit. If the scene is still open and below `soft_min_chars`, continue unless the user explicitly requested a short answer. Detect premature closure phrases such as “这一章就此”, “至于未来”, “一切仍在继续”, and “属于他们的故事才刚刚开始” as a signal for continuation or end rewrite; they are not universally forbidden when a real scene has ended.

Chunk 1–3 must not manufacture a chapter summary or ending just because their individual call ended. `very_long` may take two to four chunks but never means unlimited generation.

## 6. Seam audit

The merge step must inspect 300–800 characters around each boundary. Remove exact or high-similarity overlap, including repeated actions such as “他走到门口 / 他走到门口，然后……”. Reject or regenerate a Chunk when it reintroduces characters, summarizes earlier text, changes POV or tense, moves time backwards, rolls back relationship state, or breaks the paragraph style signature. Use one stable `event_id` per major relationship event and commit its delta only after the final merge, so a continuation cannot trigger “first confession” twice.

## 7. Isolation and observability

The host should expose a diagnostic record without placing it in story text:

```json
{
  "skill": "qwen-romance",
  "gate": "ACTIVE",
  "output_mode": "long",
  "chunks": 2,
  "story_chars": 7821,
  "continuation_reason": "scene_open",
  "runtime_parameter": "n_predict",
  "committed_event_ids": ["first_confession_001"]
}
```

For GPT/OpenAI, non-Qwen, and unknown models the expected diagnostic remains `gate=INACTIVE`, `loaded_modules=0`; no controller or prompt rule from this contract may be loaded.

