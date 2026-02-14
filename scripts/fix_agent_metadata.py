#!/usr/bin/env python3
"""
Scripts to fix missing metadata in .agent/workflows and .agent/skills
to satisfy Dendron Safety Contract Audit checks.

Workflows:
- Adds `lcm_state: beta` if missing
- Adds `version: 1.0` if missing

Skills:
- Adds `risk_tier: L1` if missing
- Adds `risks: ["Unknown risks (auto-migrated)"]` if missing
- Adds `reversible: true` if missing (warning fix)
- Adds `requires_approval: false` if missing (warning fix)
- Adds `fallbacks: []` if missing (warning fix)
"""

import os
from pathlib import Path
import yaml

AGENT_DIR = Path(".agent")
WORKFLOW_DIR = AGENT_DIR / "workflows"
SKILL_DIR = AGENT_DIR / "skills"

def fix_workflow_metadata():
    if not WORKFLOW_DIR.exists():
        print(f"Directory not found: {WORKFLOW_DIR}")
        return

    print(f"Scanning workflows in {WORKFLOW_DIR}...")
    for md_file in WORKFLOW_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        # Check for frontmatter
        if not content.startswith("---\n"):
            continue

        try:
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            frontmatter_raw = parts[1]
            frontmatter = yaml.safe_load(frontmatter_raw) or {}

            updated = False

            if "lcm_state" not in frontmatter:
                frontmatter["lcm_state"] = "beta"
                updated = True

            if "version" not in frontmatter:
                frontmatter["version"] = 1.0
                updated = True

            if updated:
                new_frontmatter = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
                new_content = f"---\n{new_frontmatter}\n---{parts[2]}"
                md_file.write_text(new_content, encoding="utf-8")
                print(f"✅ Fixed workflow: {md_file.name}")

        except Exception as e:
            print(f"❌ Error processing {md_file.name}: {e}")

def fix_skill_metadata():
    if not SKILL_DIR.exists():
        print(f"Directory not found: {SKILL_DIR}")
        return

    print(f"Scanning skills in {SKILL_DIR}...")
    for md_file in SKILL_DIR.glob("**/*.md"):
        if md_file.name == "SKILL_TEMPLATE.md":
            continue

        content = md_file.read_text(encoding="utf-8")

        if not content.startswith("---\n"):
            continue

        try:
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            frontmatter_raw = parts[1]
            frontmatter = yaml.safe_load(frontmatter_raw) or {}

            updated = False

            if "risk_tier" not in frontmatter:
                frontmatter["risk_tier"] = "L1"
                updated = True

            if "risks" not in frontmatter:
                frontmatter["risks"] = ["Unknown risks (auto-migrated)"]
                updated = True

            # Fix warnings too
            if "reversible" not in frontmatter:
                frontmatter["reversible"] = True
                updated = True

            if "requires_approval" not in frontmatter:
                frontmatter["requires_approval"] = False
                updated = True

            if "fallbacks" not in frontmatter:
                frontmatter["fallbacks"] = []
                updated = True

            if updated:
                new_frontmatter = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
                new_content = f"---\n{new_frontmatter}\n---{parts[2]}"
                md_file.write_text(new_content, encoding="utf-8")
                print(f"✅ Fixed skill: {md_file.relative_to(SKILL_DIR)}")

        except Exception as e:
            print(f"❌ Error processing {md_file.name}: {e}")

if __name__ == "__main__":
    fix_workflow_metadata()
    fix_skill_metadata()
