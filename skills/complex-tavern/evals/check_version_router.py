#!/usr/bin/env python3
"""Static gate for existing-@ Cloud Version Router; not a host integration test."""
from pathlib import Path
import json
import re
import sys
import urllib.request
ROOT = Path(__file__).resolve().parents[3]
SOURCE = (ROOT / "skills/complex-tavern/SKILL.md").read_text(encoding="utf-8")
INDEX = (ROOT / "skills/README.md").read_text(encoding="utf-8")
HOME = (ROOT / "README.md").read_text(encoding="utf-8")
tests = {
  "stable YAML retained": SOURCE.startswith("---\nname: complex-tavern-engine-v3\n"),
  "router version shown in frontmatter": "version: 3.7.2\nstatus: stable-default" in SOURCE.split("---",2)[1],
  "same stable canonical path": "canonical_path: skills/complex-tavern/SKILL.md" in SOURCE,
  "standalone router present": SOURCE.count("### 0.1.3 Cloud Version Router") == 1,
  "A v3 path": "A. 稳定版 v3" in SOURCE and "main:skills/complex-tavern/SKILL.md" in SOURCE,
  "B v4 cloud branch path": "B. Muse × GPT-6 v4 Demo" in SOURCE and
      "feat/complex-tavern-muse-gpt6-20261014:skills/complex-tavern-v4-demo/SKILL.md" in SOURCE,
  "first visible version banner retained": "0.1.2 的**入口**版本确认" in SOURCE,
  "no silent default to v3": "不静默直接开始 v3 剧情" in SOURCE,
  "explicit version skip menu": "省略版本菜单直接路由" in SOURCE,
  "branch selected as explicitly chosen v4": "明确选择 v4 Demo 及其指定 Git ref" in SOURCE,
  "v4 must fetch complete source": "读取**完整** v4 Demo" in SOURCE,
  "v4 source failure fail closed": "不回退使用缓存当作新版" in SOURCE,
  "v4 is never falsely main canonical": "非 main canonical 最新版" in SOURCE,
  "session choices stick": "不每轮重复显示菜单" in SOURCE,
  "menu meta not game choice": "版本菜单内的 A/B 是元选择" in SOURCE,
  "no story read or migration": "不扫描、不打开、不上传、不改写任何私人剧情" in SOURCE,
  "v3 relationship gates remain": "#### 1.1.3 Age / Relationship Gate" in SOURCE,
  "v3 opening state machine remains": "#### 1.1.1 Opening State Machine" in SOURCE,
  "home index updated": "云端版本选择" in HOME and "3.7.2" in HOME,
  "skills index updated": "Cloud version menu" in INDEX and "3.7.2" in INDEX,
  "no added direct story files": not any(p.is_file() and (
      p.name.lower()=="state.md" or p.name.lower().startswith("story-") or "raw-story" in p.name.lower()
    ) for p in (ROOT/"skills/complex-tavern").rglob("*")),
}
if "--remote" in sys.argv:
    url="https://raw.githubusercontent.com/1948666760dty-sys/agent-skills/feat/complex-tavern-muse-gpt6-20261014/skills/complex-tavern-v4-demo/SKILL.md"
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"complex-tavern-router-check"}),timeout=20) as response:
            remote=response.read().decode("utf-8")
        tests["v4 branch exists and is fully integrated"]=all(s in remote for s in (
            "version: 4.0.0-demo.6","## 21. Muse × GPT-6","status: experimental-demo"))
    except Exception as e:
        tests["v4 branch exists and is fully integrated"]=False
        print("remote lookup failed:",type(e).__name__,str(e),file=sys.stderr)
failed=[k for k,v in tests.items() if not v]
print(json.dumps({"status":"PASS" if not failed else "FAIL",
                  "pass":len(tests)-len(failed),"total":len(tests),
                  "failed":failed,
                  "limitations":"STATIC ROUTER VALIDATION ONLY; NOT AN INSTALLED @ RUNTIME TEST"},
                  ensure_ascii=False,indent=2))
if failed: sys.exit(1)
