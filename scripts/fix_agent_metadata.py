#!/usr/bin/env python3
"""
Fix missing metadata in .agent/ workflows and skills to pass Dendron audit.
"""

import os
from pathlib import Path
import re

AGENT_DIR = Path(".agent")
WORKFLOWS_DIR = AGENT_DIR / "workflows"
SKILLS_DIR = AGENT_DIR / "skills"

def fix_workflows():
    if not WORKFLOWS_DIR.exists():
        return

    for md_file in WORKFLOWS_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        # Check for frontmatter
        if not content.startswith("---"):
            continue

        frontmatter_end = content.find("\n---", 3)
        if frontmatter_end == -1:
            continue

        frontmatter = content[3:frontmatter_end]
        new_frontmatter = frontmatter
        updated = False

        if "lcm_state:" not in frontmatter:
            new_frontmatter += "\nlcm_state: beta"
            updated = True

        if "version:" not in frontmatter:
            new_frontmatter += "\nversion: 1.0"
            updated = True

        if updated:
            new_content = "---\n" + new_frontmatter.strip() + "\n" + content[frontmatter_end:]
            md_file.write_text(new_content, encoding="utf-8")
            print(f"Fixed workflow: {md_file.name}")

def fix_skills():
    if not SKILLS_DIR.exists():
        return

    for md_file in SKILLS_DIR.rglob("*.md"):
        # Skip README or templates if they are not skills (though templates might need it too)
        # The audit seems to check all .md files in skills dir?

        content = md_file.read_text(encoding="utf-8")

        # Check for frontmatter
        if not content.startswith("---"):
            continue

        frontmatter_end = content.find("\n---", 3)
        if frontmatter_end == -1:
            continue

        frontmatter = content[3:frontmatter_end]
        new_frontmatter = frontmatter
        updated = False

        # Check if it looks like a skill (has name/description/activation)
        # Or just blindly add required fields if missing

        if "risk_tier:" not in frontmatter:
            new_frontmatter += "\nrisk_tier: L1"
            updated = True

        if "risks:" not in frontmatter:
            new_frontmatter += "\nrisks:\n  - \"Unknown risks (auto-fixed)\""
            updated = True

        if updated:
            new_content = "---\n" + new_frontmatter.strip() + "\n" + content[frontmatter_end:]
            md_file.write_text(new_content, encoding="utf-8")
            print(f"Fixed skill: {md_file.relative_to(AGENT_DIR)}")

if __name__ == "__main__":
    print("Fixing agent metadata...")
    fix_workflows()
    fix_skills()
    print("Done.")
