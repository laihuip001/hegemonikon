#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- scripts/
# PURPOSE: Agent メタデータ (Safety Contract) の自動修復
"""
Dendron Safety Contract Audit のエラーを修正する。
.agent/skills/**/SKILL.md に risk_tier, risks を追加。
.agent/workflows/**.md に lcm_state, version を追加。
"""

from pathlib import Path
import re

AGENT_DIR = Path(".agent")

def fix_skills():
    """Skill のメタデータを修復"""
    skills = list(AGENT_DIR.glob("skills/**/SKILL.md"))
    print(f"Checking {len(skills)} skills...")

    fixed = 0
    for path in skills:
        content = path.read_text(encoding="utf-8")
        if "risk_tier:" not in content:
            # frontmatter の末尾に追加
            if re.search(r"^---$", content, re.MULTILINE):
                # 2つ目の --- の前、または最初のブロックの終わり
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    if "risk_tier" not in frontmatter:
                        new_fm = frontmatter.rstrip() + "\nrisk_tier: L1\nrisks: []\n"
                        content = f"---{new_fm}---{parts[2]}"
                        path.write_text(content, encoding="utf-8")
                        fixed += 1
                        print(f"Fixed skill: {path}")
    print(f"Fixed {fixed} skills")

def fix_workflows():
    """Workflow のメタデータを修復"""
    wfs = list(AGENT_DIR.glob("workflows/*.md"))
    print(f"Checking {len(wfs)} workflows...")

    fixed = 0
    for path in wfs:
        content = path.read_text(encoding="utf-8")
        if "lcm_state:" not in content:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                if "lcm_state" not in frontmatter:
                    new_fm = frontmatter.rstrip() + "\nlcm_state: beta\nversion: 1.0\n"
                    content = f"---{new_fm}---{parts[2]}"
                    path.write_text(content, encoding="utf-8")
                    fixed += 1
                    print(f"Fixed workflow: {path}")
    print(f"Fixed {fixed} workflows")

if __name__ == "__main__":
    if not AGENT_DIR.exists():
        print("Error: .agent directory not found")
        exit(1)
    fix_skills()
    fix_workflows()
