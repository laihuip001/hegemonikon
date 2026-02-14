#!/usr/bin/env python3
"""
Fix missing metadata in .agent/skills and .agent/workflows to satisfy Dendron Safety Contract.

Skills:
  - Adds `risk_tier: L1` (default)
  - Adds `risks: []` (default)

Workflows:
  - Adds `lcm_state: beta` (default)
  - Adds `version: "1.0"` (default)
"""

import os
from pathlib import Path
import yaml

AGENT_ROOT = Path(".agent")
SKILLS_DIR = AGENT_ROOT / "skills"
WORKFLOWS_DIR = AGENT_ROOT / "workflows"

def fix_skill_metadata(path: Path):
    """Fix missing metadata in skill markdown file."""
    try:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return # Skip if no frontmatter

        parts = content.split("---", 2)
        if len(parts) < 3:
            return

        frontmatter_raw = parts[1]
        body = parts[2]

        try:
            data = yaml.safe_load(frontmatter_raw) or {}
        except yaml.YAMLError:
            print(f"Skipping {path}: Invalid YAML")
            return

        changed = False
        if "risk_tier" not in data:
            data["risk_tier"] = "L1"
            changed = True
        if "risks" not in data:
            data["risks"] = []
            changed = True

        if changed:
            new_frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False).strip()
            new_content = f"---\n{new_frontmatter}\n---{body}"
            path.write_text(new_content, encoding="utf-8")
            print(f"Fixed skill: {path}")

    except Exception as e:
        print(f"Error processing {path}: {e}")

def fix_workflow_metadata(path: Path):
    """Fix missing metadata in workflow markdown file."""
    try:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return

        parts = content.split("---", 2)
        if len(parts) < 3:
            return

        frontmatter_raw = parts[1]
        body = parts[2]

        try:
            data = yaml.safe_load(frontmatter_raw) or {}
        except yaml.YAMLError:
            print(f"Skipping {path}: Invalid YAML")
            return

        changed = False
        if "lcm_state" not in data:
            data["lcm_state"] = "beta"
            changed = True
        if "version" not in data:
            data["version"] = "1.0"
            changed = True

        if changed:
            new_frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False).strip()
            new_content = f"---\n{new_frontmatter}\n---{body}"
            path.write_text(new_content, encoding="utf-8")
            print(f"Fixed workflow: {path}")

    except Exception as e:
        print(f"Error processing {path}: {e}")

def main():
    if not AGENT_ROOT.exists():
        print(f"Agent root not found: {AGENT_ROOT}")
        return

    # Process Skills
    if SKILLS_DIR.exists():
        for md_file in SKILLS_DIR.glob("**/*.md"):
            if md_file.name == "SKILL_TEMPLATE.md":
                continue
            fix_skill_metadata(md_file)

    # Process Workflows
    if WORKFLOWS_DIR.exists():
        for md_file in WORKFLOWS_DIR.glob("*.md"):
            fix_workflow_metadata(md_file)

if __name__ == "__main__":
    main()
