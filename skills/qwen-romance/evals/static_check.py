#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[3]
skill = ROOT / "skills/qwen-romance/SKILL.md"
evals = ROOT / "skills/qwen-romance/evals/evals.json"
long_output_evals = ROOT / "skills/qwen-romance/evals/long-output-cases.json"
schema = ROOT / "skills/qwen-romance/references/state.schema.json"

errors = []
for p in (skill, evals, long_output_evals, schema):
    if not p.exists():
        errors.append(f"missing: {p.relative_to(ROOT)}")

if skill.exists():
    s = skill.read_text(encoding="utf-8")
    required = [
        "name: qwen-romance",
        "version: 0.2.0",
        "activation: qwen-local-only-fail-closed",
        "GPT/OpenAI 永远 INACTIVE",
        "unknown model => inactive",
        "max_intensity",
        "current_intensity",
        "AGE GATE",
        "CONSENT GATE",
        "CAPACITY GATE",
        "release-candidate",
        "Long Output Controller",
        "soft_min_chars",
        "preferred_chars",
        "max_internal_chunks",
        "premature_closure_guard",
        "token_budget",
        "GPT/OpenAI",
    ]
    for token in required:
        if token not in s:
            errors.append(f"SKILL.md missing required token: {token}")
    if "status: stable-default" in s:
        errors.append("release candidate must not claim stable-default before real Qwen smoke test")

if evals.exists():
    try:
        data = json.loads(evals.read_text(encoding="utf-8"))
        if data.get("skill") != "qwen-romance": errors.append("eval skill mismatch")
        if data.get("version") != "0.2.0": errors.append("eval version mismatch")
        names = {x.get("name") for x in data.get("cases", [])}
        for name in ["gpt_openai_hard_off","unknown_family_fail_closed","r4_max_does_not_force_current","minor_blocks_adult_layer","complex_tavern_gpt_path_unchanged"]:
            if name not in names: errors.append(f"missing eval case: {name}")
        if len(data.get("cases", [])) < 20: errors.append("expected at least 20 regression cases")
    except Exception as e:
        errors.append(f"invalid evals JSON: {e}")

if long_output_evals.exists():
    try:
        data = json.loads(long_output_evals.read_text(encoding="utf-8"))
        if data.get("skill") != "qwen-romance": errors.append("long-output eval skill mismatch")
        if data.get("version") != "0.2.0": errors.append("long-output eval version mismatch")
        names = {x.get("name") for x in data.get("cases", [])}
        required = {
            "interactive_long_under_min_open_scene",
            "novel_very_long_single_call_limit",
            "seam_overlap_removed",
            "gpt_controller_not_loaded",
            "local_qwen_controller_available",
            "dynamic_budget_preserves_context_reserve",
            "natural_stop_below_soft_min_allowed",
            "open_scene_below_soft_min_continues",
        }
        for name in required:
            if name not in names: errors.append(f"missing long-output eval case: {name}")
        if len(data.get("cases", [])) < 15: errors.append("expected at least 15 long-output regression cases")
    except Exception as e:
        errors.append(f"invalid long-output evals JSON: {e}")

if evals.exists() and long_output_evals.exists():
    try:
        base_count = len(json.loads(evals.read_text(encoding="utf-8")).get("cases", []))
        long_count = len(json.loads(long_output_evals.read_text(encoding="utf-8")).get("cases", []))
        if base_count + long_count < 40: errors.append("expected at least 40 combined regression cases")
    except Exception:
        pass

if schema.exists():
    try:
        data = json.loads(schema.read_text(encoding="utf-8"))
        enum = data["properties"]["gate"]["properties"]["model_family"]["enum"]
        if "qwen" not in enum or "unknown" not in enum: errors.append("schema model_family enum incomplete")
        if "allOf" not in data: errors.append("schema missing active=>qwen constraint")
    except Exception as e:
        errors.append(f"invalid schema JSON: {e}")

if errors:
    print("FAIL")
    for e in errors: print("-", e)
    sys.exit(1)
print("PASS: qwen-romance static checks")
