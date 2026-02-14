#!/usr/bin/env python3
"""
Fix Agent Metadata

Adds missing frontmatter fields to skills and workflows:
- Skills: risk_tier (L1), risks (TBD)
- Workflows: lcm_state (beta), version (1.0)
"""

import os
import re
from pathlib import Path

SKILLS_DIR = Path(".agent/skills")
WORKFLOWS_DIR = Path(".agent/workflows")

def fix_skills():
    if not SKILLS_DIR.exists():
        print(f"Skills dir not found: {SKILLS_DIR}")
        return

    for skill_file in SKILLS_DIR.glob("**/SKILL.md"):
        content = skill_file.read_text()

        # Check and fix frontmatter
        if content.startswith("---\n"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]

                # Check for risk_tier
                if "risk_tier:" not in frontmatter:
                    frontmatter += "risk_tier: L1\n"

                # Check for risks
                if "risks:" not in frontmatter:
                    frontmatter += "risks:\n  - description: TBD\n    severity: low\n"

                new_content = f"---{frontmatter}---{parts[2]}"
                if new_content != content:
                    skill_file.write_text(new_content)
                    print(f"Fixed skill: {skill_file}")

def fix_workflows():
    if not WORKFLOWS_DIR.exists():
        print(f"Workflows dir not found: {WORKFLOWS_DIR}")
        return

    for wf_file in WORKFLOWS_DIR.glob("*.md"):
        content = wf_file.read_text()

        # Check and fix frontmatter
        if content.startswith("---\n"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]

                # Check for lcm_state
                if "lcm_state:" not in frontmatter:
                    frontmatter += "lcm_state: beta\n"

                # Check for version
                if "version:" not in frontmatter:
                    frontmatter += "version: 1.0\n"

                new_content = f"---{frontmatter}---{parts[2]}"
                if new_content != content:
                    wf_file.write_text(new_content)
                    print(f"Fixed workflow: {wf_file}")

if __name__ == "__main__":
    fix_skills()
    fix_workflows()
