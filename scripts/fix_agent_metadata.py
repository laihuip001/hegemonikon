#!/usr/bin/env python3
"""
Fix Agent Metadata Script

Automatically adds missing required metadata fields to Agent Skills and Workflows
to satisfy the Dendron Safety Contract audit.

Targets:
- .agent/skills/**/SKILL.md: Adds 'risk_tier: L1' and 'risks: []'
- .agent/workflows/*.md: Adds 'lcm_state: beta' and 'version: 1.0'
"""

import os
import sys
from pathlib import Path
import yaml

def fix_frontmatter(path: Path, default_fields: dict) -> bool:
    """Fix YAML frontmatter in a markdown file."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return False

    if not content.startswith("---"):
        print(f"Skipping {path}: No frontmatter found")
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"Skipping {path}: Invalid frontmatter format")
        return False

    fm_text = parts[1]
    body = parts[2]

    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML in {path}: {e}")
        return False

    modified = False
    for key, value in default_fields.items():
        if key not in fm:
            fm[key] = value
            modified = True
            print(f"  + Added {key}: {value}")

    if modified:
        new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True).strip()
        new_content = f"---\n{new_fm}\n---{body}"
        path.write_text(new_content, encoding="utf-8")
        print(f"✅ Fixed {path}")
        return True

    return False

def main():
    root = Path(".agent")
    if not root.exists():
        print("Error: .agent directory not found")
        sys.exit(1)

    print("--- Fixing Skills ---")
    skills_dir = root / "skills"
    if skills_dir.exists():
        for skill_file in skills_dir.glob("**/SKILL.md"):
            fix_frontmatter(skill_file, {
                "risk_tier": "L1",
                "risks": []
            })

    print("\n--- Fixing Workflows ---")
    workflows_dir = root / "workflows"
    if workflows_dir.exists():
        for wf_file in workflows_dir.glob("*.md"):
            fix_frontmatter(wf_file, {
                "lcm_state": "beta",
                "version": "1.0"
            })

if __name__ == "__main__":
    main()
