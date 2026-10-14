#!/usr/bin/env python3
"""Static source audit for the Muse × GPT-6 integration candidate.

This checks repository rule text, packaging and privacy boundaries only.
Passing does NOT prove long-session gameplay, actual UI rendering,
Muse embed token support, atomic persistence or plugin installation.
"""
from pathlib import Path
import json
import re
import sys

DEMO = Path(__file__).resolve().parents[1]
root = DEMO / "SKILL.md"
text = root.read_text(encoding="utf-8")

def contents(path):
    return (DEMO / path).read_text(encoding="utf-8")

files = {
    "README.md": contents("README.md"),
    "docs/INTEGRATION_GUIDE.md": contents("docs/INTEGRATION_GUIDE.md"),
    "docs/RULE_CONFLICTS.md": contents("docs/RULE_CONFLICTS.md"),
    "docs/PLATFORM_ADAPTER_CONTRACT.md": contents("docs/PLATFORM_ADAPTER_CONTRACT.md"),
    "adapters/muse.md": contents("adapters/muse.md"),
    "adapters/gpt6.md": contents("adapters/gpt6.md"),
    "cards/CARDS.md": contents("cards/CARDS.md"),
    "ops/CHANGELOG.md": contents("ops/CHANGELOG.md"),
    "ops/ERRORS.md": contents("ops/ERRORS.md"),
    "ops/PRIVACY_POLICY.md": contents("ops/PRIVACY_POLICY.md"),
    "evals/TESTPLAN_ADAPTERS.md": contents("evals/TESTPLAN_ADAPTERS.md"),
}

tests = {
    "frontmatter intact": text.startswith("---\n") and "version: 4.0.0-demo.6" in text.split("---", 2)[1],
    "schema unchanged": "4.0-demo.4" in text,
    "original engine sections preserved": all(needle in text for needle in [
        "Single Authority", "Context Composer", "Action Queue",
        "Cast Identity", "NPC Knowledge", "Final Visible Handoff",
        "Commit Protocol", "## 20.",
    ]),
    "one unified Section 21": text.count("## 21. Muse × GPT-6") == 1,
    "core is not a second authority": "不具备直接写 Canon" in text,
    "default stable route stays isolated": "普通“开始/继续复杂酒馆”仍由 stable" in text,
    "canonical verification retained": "0.1.2" in text and "GitHub 主源" in text,
    "compact expanded freeform profiles": "menu_profile = compact | expanded | freeform" in text,
    "no artificial twenty options": "不能硬塞无关动作" in text,
    "freeform needs explicit choice": "freeform 必须用户明确" in text,
    "mandatory preflight preserved": "Director Preflight / Final Visible Handoff" in text,
    "extra self-check does not spend story turn": "0次/1次/2次" in text and "不推进时间" in text,
    "gate bound choice mapping": "gate_id/option_id" in text,
    "sequenced action queue": "先D再C" in text,
    "adult consent age restrictions": "C1/C2 和年龄门" in text and "角色意愿、同意、年龄" in text,
    "calendar safeguards": "跨天决定" in text and "星期" in text,
    "POV and NPC private state separation": "second_person_limited" in text and "NPC 私密内心" in text,
    "dream world contract exception": "ordinary_isolated" in text and "World Contract" in text,
    "no in-narrative scene ID": "S+数字" in text,
    "unknown character identity supported": "name_source" in text and "unknown" in text,
    "must not fabricate embed token": "embed_token" in text and "不能伪造" in text,
    "fictional map honesty": "不得将虚构坐标包装为真实地图定位" in text,
    "real menu before four-line footer": "decision_required / scope_boundary" in text and "四行状态收尾" in text,
    "private saves must not enter public repo": "STATE.md" in text and "严禁上传" in text,
    "adapter does not claim original Muse UI completed": "尚未取得" in files["cards/CARDS.md"],
    "GPT-6 has fallback interaction": "文本 A–T" in files["adapters/gpt6.md"],
    "Muse adapter refuses fake token": "不可编造" in files["adapters/muse.md"],
    "conflict matrix is present": "Muse 每轮20项" in files["docs/RULE_CONFLICTS.md"],
    "regression limitations marked": "NOT_TESTED" in files["evals/TESTPLAN_ADAPTERS.md"],
    "no story or state files in demo": not any(
        p.name.lower() == "state.md" or
        p.name.lower().startswith("story-") or
        p.name.lower() == "raw-story-log.md"
        for p in DEMO.rglob("*") if p.is_file()
    ),
    "no story paths in documents": all(
        "/TavernSavesV4/" not in value or key == "README.md"
        for key, value in files.items()
    ),
}
failed = [name for name, passed in tests.items() if not passed]
print(json.dumps({
    "scope": "STATIC_SOURCE_ONLY",
    "status": "PASS" if not failed else "FAIL",
    "total": len(tests),
    "passed": len(tests) - len(failed),
    "failed": failed,
    "limitations": ["NO_LIVE_GPT6_TEST", "NO_LIVE_MUSE_TEST", "NO_PERSISTENCE_TEST"]
}, ensure_ascii=False, indent=2))
if failed:
    sys.exit(1)
