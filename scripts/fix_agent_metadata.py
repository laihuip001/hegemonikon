#!/usr/bin/env python3
"""
Fix Agent Metadata

Adds missing metadata fields to Agent Skills and Workflows to satisfy Dendron Safety Contract audits.

Target:
  - .agent/skills/**/SKILL.md
    - risk_tier: "L1" (default)
    - risks: [] (default)
  - .agent/workflows/**.md
    - lcm_state: "beta" (default)
    - version: "1.0" (default)

Usage:
  python scripts/fix_agent_metadata.py
"""

import os
import re
from pathlib import Path

# Default values
DEFAULT_RISK_TIER = "L1"
DEFAULT_RISKS = "[]"
DEFAULT_LCM_STATE = "beta"
DEFAULT_VERSION = "1.0"

def fix_skill(path: Path):
    """Add missing metadata to SKILL.md"""
    content = path.read_text(encoding="utf-8")

    # Check for frontmatter
    if not content.startswith("---\n"):
        print(f"⚠️  Skipping {path}: No frontmatter found")
        return

    # Extract frontmatter
    try:
        fm_end = content.index("\n---", 4)
        frontmatter = content[4:fm_end]
        body = content[fm_end:]
    except ValueError:
        print(f"⚠️  Skipping {path}: Invalid frontmatter format")
        return

    updated = False

    # Check risk_tier
    if "risk_tier:" not in frontmatter:
        frontmatter += f"\nrisk_tier: {DEFAULT_RISK_TIER}"
        updated = True

    # Check risks
    if "risks:" not in frontmatter:
        frontmatter += f"\nrisks: {DEFAULT_RISKS}"
        updated = True

    if updated:
        new_content = f"---\n{frontmatter}{body}"
        path.write_text(new_content, encoding="utf-8")
        print(f"✅ Fixed Skill: {path}")

def fix_workflow(path: Path):
    """Add missing metadata to workflow .md"""
    content = path.read_text(encoding="utf-8")

    # Check for frontmatter
    if not content.startswith("---\n"):
        print(f"⚠️  Skipping {path}: No frontmatter found")
        return

    # Extract frontmatter
    try:
        fm_end = content.index("\n---", 4)
        frontmatter = content[4:fm_end]
        body = content[fm_end:]
    except ValueError:
        print(f"⚠️  Skipping {path}: Invalid frontmatter format")
        return

    updated = False

    # Check lcm_state
    if "lcm_state:" not in frontmatter:
        frontmatter += f"\nlcm_state: {DEFAULT_LCM_STATE}"
        updated = True

    # Check version
    if "version:" not in frontmatter:
        frontmatter += f"\nversion: {DEFAULT_VERSION}"
        updated = True

    if updated:
        new_content = f"---\n{frontmatter}{body}"
        path.write_text(new_content, encoding="utf-8")
        print(f"✅ Fixed Workflow: {path}")

def main():
    root = Path(".agent")
    if not root.exists():
        print("❌ .agent directory not found")
        return

    print("🔧 Fixing Agent Metadata...")

    # Skills
    skills_dir = root / "skills"
    if skills_dir.exists():
        for skill_file in skills_dir.rglob("SKILL.md"):
            fix_skill(skill_file)

    # Workflows
    workflows_dir = root / "workflows"
    if workflows_dir.exists():
        for wf_file in workflows_dir.glob("*.md"):
            fix_workflow(wf_file)

    print("✨ Done.")

if __name__ == "__main__":
    main()
