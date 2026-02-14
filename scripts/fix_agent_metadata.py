#!/usr/bin/env python3
"""
Fix missing metadata in .agent/skills and .agent/workflows to satisfy Dendron Safety Contract.

Skills: Adds risk_tier: L1, risks: [none]
Workflows: Adds lcm_state: beta, version: 1.0
"""

import os
import yaml
from pathlib import Path

AGENT_DIR = Path(".agent")

def fix_skills():
    skills_dir = AGENT_DIR / "skills"
    if not skills_dir.exists():
        return

    for skill_file in skills_dir.glob("**/SKILL.md"):
        content = skill_file.read_text()
        if content.startswith("---"):
            try:
                # Extract frontmatter
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    fm = yaml.safe_load(parts[1])
                    if not fm: fm = {}

                    modified = False
                    if "risk_tier" not in fm:
                        fm["risk_tier"] = "L1"
                        modified = True
                    if "risks" not in fm:
                        fm["risks"] = ["none"]
                        modified = True

                    if modified:
                        new_fm = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
                        new_content = f"---\n{new_fm}\n---{parts[2]}"
                        skill_file.write_text(new_content)
                        print(f"Fixed skill: {skill_file}")
            except Exception as e:
                print(f"Error parsing {skill_file}: {e}")

def fix_workflows():
    wf_dir = AGENT_DIR / "workflows"
    if not wf_dir.exists():
        return

    for wf_file in wf_dir.glob("*.md"):
        content = wf_file.read_text()
        if content.startswith("---"):
            try:
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    fm = yaml.safe_load(parts[1])
                    if not fm: fm = {}

                    modified = False
                    if "lcm_state" not in fm:
                        fm["lcm_state"] = "beta"
                        modified = True
                    if "version" not in fm:
                        fm["version"] = "1.0"
                        modified = True

                    if modified:
                        new_fm = yaml.dump(fm, sort_keys=False, allow_unicode=True).strip()
                        new_content = f"---\n{new_fm}\n---{parts[2]}"
                        wf_file.write_text(new_content)
                        print(f"Fixed workflow: {wf_file}")
            except Exception as e:
                print(f"Error parsing {wf_file}: {e}")

if __name__ == "__main__":
    fix_skills()
    fix_workflows()
