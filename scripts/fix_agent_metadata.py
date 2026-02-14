#!/usr/bin/env python3
"""
Fix Agent Metadata

Iterates through .agent/skills/ and .agent/workflows/ to ensure mandatory metadata exists.
- Skills: risk_tier: L1, risks: []
- Workflows: lcm_state: beta, version: "1.0"
"""

import sys
from pathlib import Path
import yaml

AGENT_ROOT = Path(".agent")
SKILLS_ROOT = AGENT_ROOT / "skills"
WORKFLOWS_ROOT = AGENT_ROOT / "workflows"

def fix_skill_metadata(path: Path):
    try:
        content = path.read_text()
        if content.startswith("---"):
            # Existing frontmatter
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1]) or {}

                updated = False
                if "risk_tier" not in frontmatter:
                    frontmatter["risk_tier"] = "L1"
                    updated = True
                if "risks" not in frontmatter:
                    frontmatter["risks"] = []
                    updated = True

                if updated:
                    new_fm = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
                    new_content = f"---\n{new_fm}---\n{parts[2]}"
                    path.write_text(new_content)
                    print(f"Fixed skill: {path}")
        else:
            # No frontmatter, prepend it
            frontmatter = {
                "risk_tier": "L1",
                "risks": []
            }
            new_fm = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
            new_content = f"---\n{new_fm}---\n\n{content}"
            path.write_text(new_content)
            print(f"Added frontmatter to skill: {path}")

    except Exception as e:
        print(f"Error processing {path}: {e}")

def fix_workflow_metadata(path: Path):
    try:
        content = path.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1]) or {}

                updated = False
                if "lcm_state" not in frontmatter:
                    frontmatter["lcm_state"] = "beta"
                    updated = True
                if "version" not in frontmatter:
                    frontmatter["version"] = "1.0"
                    updated = True

                if updated:
                    new_fm = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
                    new_content = f"---\n{new_fm}---\n{parts[2]}"
                    path.write_text(new_content)
                    print(f"Fixed workflow: {path}")
        else:
            frontmatter = {
                "lcm_state": "beta",
                "version": "1.0"
            }
            new_fm = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
            new_content = f"---\n{new_fm}---\n\n{content}"
            path.write_text(new_content)
            print(f"Added frontmatter to workflow: {path}")

    except Exception as e:
        print(f"Error processing {path}: {e}")

def main():
    if not SKILLS_ROOT.exists():
        print(f"Skills root not found: {SKILLS_ROOT}")
        return

    # Process Skills
    for md_file in SKILLS_ROOT.glob("**/SKILL.md"):
        fix_skill_metadata(md_file)

    # Process Workflows
    if WORKFLOWS_ROOT.exists():
        for md_file in WORKFLOWS_ROOT.glob("*.md"):
            fix_workflow_metadata(md_file)

if __name__ == "__main__":
    main()
