#!/usr/bin/env python3
# PURPOSE: Fix missing metadata in .agent/ skills and workflows
import os
from pathlib import Path
import yaml  # requires pyyaml

def fix_skills():
    root = Path(".agent/skills")
    if not root.exists():
        return

    for skill_file in root.glob("**/SKILL.md"):
        content = skill_file.read_text()

        # Check if YAML frontmatter exists
        if content.startswith("---\n"):
            # Simple check for missing fields
            if "risk_tier:" not in content:
                print(f"Fixing risk_tier in {skill_file}")
                content = content.replace("---\n", "---\nrisk_tier: L1\n", 1)

            if "risks:" not in content:
                print(f"Fixing risks in {skill_file}")
                content = content.replace("---\n", "---\nrisks:\n  - General operational risk\n", 1)

            skill_file.write_text(content)
        else:
            print(f"No frontmatter in {skill_file}, skipping auto-fix")

def fix_workflows():
    root = Path(".agent/workflows")
    if not root.exists():
        return

    for wf_file in root.glob("*.md"):
        content = wf_file.read_text()

        if content.startswith("---\n"):
            if "lcm_state:" not in content:
                print(f"Fixing lcm_state in {wf_file}")
                content = content.replace("---\n", "---\nlcm_state: beta\n", 1)

            if "version:" not in content:
                print(f"Fixing version in {wf_file}")
                content = content.replace("---\n", "---\nversion: 1.0.0\n", 1)

            wf_file.write_text(content)
        else:
            print(f"No frontmatter in {wf_file}, skipping auto-fix")

if __name__ == "__main__":
    fix_skills()
    fix_workflows()
