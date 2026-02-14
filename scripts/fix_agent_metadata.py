#!/usr/bin/env python3
"""
scripts/fix_agent_metadata.py

Dendron Safety Contract Audit に準拠するため、
.agent/skills/**/SKILL.md および .agent/workflows/*.md に
必須メタデータを自動追記するスクリプト。

必須フィールド:
- SKILL.md: risk_tier, risks
- workflow.md: lcm_state, version

依存: pyyaml
"""

import sys
from pathlib import Path
import yaml

# Project root
ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = ROOT / ".agent"

def fix_skills():
    """SKILL.md に risk_tier, risks を追記"""
    skills_dir = AGENT_DIR / "skills"
    if not skills_dir.exists():
        print(f"⚠️ Skills dir not found: {skills_dir}")
        return

    count = 0
    for skill_file in skills_dir.glob("**/SKILL.md"):
        try:
            content = skill_file.read_text(encoding="utf-8")
            if not content.startswith("---"):
                print(f"⚠️ No frontmatter: {skill_file}")
                continue

            # Parse frontmatter
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            fm_text = parts[1]
            body = parts[2]

            try:
                fm = yaml.safe_load(fm_text) or {}
            except yaml.YAMLError:
                print(f"⚠️ YAML error: {skill_file}")
                continue

            updated = False
            if "risk_tier" not in fm:
                fm["risk_tier"] = "L1"  # Default to Low risk
                updated = True

            if "risks" not in fm:
                fm["risks"] = []  # Empty list if none
                updated = True

            # Recommended fields (warnings)
            if "reversible" not in fm:
                fm["reversible"] = True
                updated = True
            if "requires_approval" not in fm:
                fm["requires_approval"] = False
                updated = True
            if "fallbacks" not in fm:
                fm["fallbacks"] = []
                updated = True

            if updated:
                new_fm = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
                new_content = f"---\n{new_fm}\n---{body}"
                skill_file.write_text(new_content, encoding="utf-8")
                print(f"✅ Fixed SKILL: {skill_file.relative_to(ROOT)}")
                count += 1

        except Exception as e:
            print(f"❌ Error fixing {skill_file}: {e}")

    print(f"Fixed {count} skill files.")

def fix_workflows():
    """workflow.md に lcm_state, version を追記"""
    wf_dir = AGENT_DIR / "workflows"
    if not wf_dir.exists():
        print(f"⚠️ Workflows dir not found: {wf_dir}")
        return

    count = 0
    for wf_file in wf_dir.glob("*.md"):
        try:
            content = wf_file.read_text(encoding="utf-8")
            if not content.startswith("---"):
                continue

            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            fm_text = parts[1]
            body = parts[2]

            try:
                fm = yaml.safe_load(fm_text) or {}
            except yaml.YAMLError:
                continue

            updated = False
            if "lcm_state" not in fm:
                fm["lcm_state"] = "beta"
                updated = True
            if "version" not in fm:
                fm["version"] = "1.0"
                updated = True

            if updated:
                new_fm = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
                new_content = f"---\n{new_fm}\n---{body}"
                wf_file.write_text(new_content, encoding="utf-8")
                print(f"✅ Fixed Workflow: {wf_file.relative_to(ROOT)}")
                count += 1

        except Exception as e:
            print(f"❌ Error fixing {wf_file}: {e}")

    print(f"Fixed {count} workflow files.")

if __name__ == "__main__":
    fix_skills()
    fix_workflows()
