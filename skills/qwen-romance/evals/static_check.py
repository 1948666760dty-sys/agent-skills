#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[3]
skill = ROOT / "skills/qwen-romance/SKILL.md"
evals = ROOT / "skills/qwen-romance/evals/evals.json"
schema = ROOT / "skills/qwen-romance/references/state.schema.json"

errors = []
for p in (skill, evals, schema):
    if not p.exists():
        errors.append(f"missing: {p.relative_to(ROOT)}")

if skill.exists():
    s = skill.read_text(encoding="utf-8")
    required = [
        "name: qwen-romance",
        "version: 0.1.0",
        "activation: qwen-local-only-fail-closed",
        "GPT/OpenAI 永远 INACTIVE",
        "unknown model => inactive",
        "max_intensity",
        "current_intensity",
        "AGE GATE",
        "CONSENT GATE",
        "CAPACITY GATE",
        "release-candidate",
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
        if data.get("version") != "0.1.0": errors.append("eval version mismatch")
        names = {x.get("name") for x in data.get("cases", [])}
        for name in ["gpt_openai_hard_off","unknown_family_fail_closed","r4_max_does_not_force_current","minor_blocks_adult_layer","complex_tavern_gpt_path_unchanged"]:
            if name not in names: errors.append(f"missing eval case: {name}")
        if len(data.get("cases", [])) < 20: errors.append("expected at least 20 regression cases")
    except Exception as e:
        errors.append(f"invalid evals JSON: {e}")

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
