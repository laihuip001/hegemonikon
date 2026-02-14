#!/usr/bin/env python3
"""
Fix Agent Metadata Script

Bulk updates .agent/skills and .agent/workflows markdown files to ensure
compliance with Dendron Safety Contract (risk_tier, risks, lcm_state, version).
"""

import os
import re
from pathlib import Path

# Paths
AGENT_DIR = Path(".agent")
SKILLS_DIR = AGENT_DIR / "skills"
WORKFLOWS_DIR = AGENT_DIR / "workflows"

# Defaults
DEFAULT_RISK_TIER = "L1"
DEFAULT_RISKS = "[]"
DEFAULT_LCM_STATE = "beta"
DEFAULT_VERSION = "1.0"

def fix_skill(path: Path):
    """Ensure risk_tier and risks exist in skill frontmatter."""
    content = path.read_text(encoding="utf-8")

    # Check for frontmatter
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        print(f"Skipping {path}: No frontmatter found")
        return

    frontmatter = match.group(1)
    new_frontmatter = frontmatter
    modified = False

    if "risk_tier:" not in frontmatter:
        new_frontmatter += f"\nrisk_tier: {DEFAULT_RISK_TIER}"
        modified = True

    if "risks:" not in frontmatter:
        new_frontmatter += f"\nrisks: {DEFAULT_RISKS}"
        modified = True

    if modified:
        new_content = content.replace(frontmatter, new_frontmatter, 1)
        path.write_text(new_content, encoding="utf-8")
        print(f"Fixed skill: {path}")

def fix_workflow(path: Path):
    """Ensure lcm_state and version exist in workflow frontmatter."""
    content = path.read_text(encoding="utf-8")

    # Check for frontmatter
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        print(f"Skipping {path}: No frontmatter found")
        return

    frontmatter = match.group(1)
    new_frontmatter = frontmatter
    modified = False

    if "lcm_state:" not in frontmatter:
        new_frontmatter += f"\nlcm_state: {DEFAULT_LCM_STATE}"
        modified = True

    if "version:" not in frontmatter:
        new_frontmatter += f"\nversion: {DEFAULT_VERSION}"
        modified = True

    if modified:
        new_content = content.replace(frontmatter, new_frontmatter, 1)
        path.write_text(new_content, encoding="utf-8")
        print(f"Fixed workflow: {path}")

def main():
    if not AGENT_DIR.exists():
        print(f"Agent directory not found: {AGENT_DIR}")
        return

    # Fix Skills
    if SKILLS_DIR.exists():
        for md_file in SKILLS_DIR.rglob("*.md"):
            if md_file.name == "SKILL.md":
                fix_skill(md_file)

    # Fix Workflows
    if WORKFLOWS_DIR.exists():
        for md_file in WORKFLOWS_DIR.glob("*.md"):
            fix_workflow(md_file)

if __name__ == "__main__":
    main()
