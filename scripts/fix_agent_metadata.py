#!/usr/bin/env python3
"""
Script to bulk fix Safety Contract metadata in agent skills and workflows.
Adds missing frontmatter fields:
- Skills: risk_tier, risks
- Workflows: lcm_state, version
"""

import os
import re
from pathlib import Path

# --- Constants ---
SKILLS_DIR = Path(".agent/skills")
WORKFLOWS_DIR = Path(".agent/workflows")

# Defaults
DEFAULT_RISK_TIER = "L1"
DEFAULT_RISKS = ["none"]
DEFAULT_LCM_STATE = "beta"
DEFAULT_VERSION = "1.0"

def fix_skill_metadata(path: Path):
    """Injects missing risk_tier and risks into SKILL.md frontmatter."""
    if not path.exists():
        return

    content = path.read_text(encoding="utf-8")

    # Check if frontmatter exists
    if not content.startswith("---"):
        print(f"⚠️ No frontmatter in {path}, skipping.")
        return

    # Check for missing fields
    has_risk_tier = "risk_tier:" in content
    has_risks = "risks:" in content

    if has_risk_tier and has_risks:
        return # Already compliant

    print(f"🔧 Fixing skill: {path}")

    # Split frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        return

    frontmatter = parts[1]

    if not has_risk_tier:
        frontmatter += f"\nrisk_tier: {DEFAULT_RISK_TIER}"

    if not has_risks:
        frontmatter += f"\nrisks:\n  - none"

    new_content = f"---{frontmatter}\n---{parts[2]}"
    path.write_text(new_content, encoding="utf-8")


def fix_workflow_metadata(path: Path):
    """Injects missing lcm_state and version into workflow .md frontmatter."""
    if not path.exists():
        return

    content = path.read_text(encoding="utf-8")

    # Check if frontmatter exists
    if not content.startswith("---"):
        # Create frontmatter if missing (some workflows might just be markdown)
        print(f"⚠️ No frontmatter in {path}, creating.")
        frontmatter = f"---\nlcm_state: {DEFAULT_LCM_STATE}\nversion: {DEFAULT_VERSION}\n---\n\n"
        path.write_text(frontmatter + content, encoding="utf-8")
        return

    # Check for missing fields
    has_lcm_state = "lcm_state:" in content
    has_version = "version:" in content

    if has_lcm_state and has_version:
        return # Already compliant

    print(f"🔧 Fixing workflow: {path}")

    # Split frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        return

    frontmatter = parts[1]

    if not has_lcm_state:
        frontmatter += f"\nlcm_state: {DEFAULT_LCM_STATE}"

    if not has_version:
        frontmatter += f"\nversion: {DEFAULT_VERSION}"

    new_content = f"---{frontmatter}\n---{parts[2]}"
    path.write_text(new_content, encoding="utf-8")


def main():
    # Fix Skills
    if SKILLS_DIR.exists():
        for skill_file in SKILLS_DIR.glob("**/SKILL.md"):
            fix_skill_metadata(skill_file)

    # Fix Workflows
    if WORKFLOWS_DIR.exists():
        for workflow_file in WORKFLOWS_DIR.glob("*.md"):
            fix_workflow_metadata(workflow_file)

if __name__ == "__main__":
    main()
