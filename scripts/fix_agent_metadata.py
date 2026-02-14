#!/usr/bin/env python3
"""
Fix missing metadata in .agent/skills and .agent/workflows to satisfy Dendron Safety Contract.

Targets:
- Skills: risk_tier (L1), risks ([])
- Workflows: lcm_state (beta), version (1.0)
"""

import os
from pathlib import Path
import yaml

AGENT_DIR = Path(".agent")

def fix_skills():
    skills_dir = AGENT_DIR / "skills"
    if not skills_dir.exists():
        return

    for skill_file in skills_dir.glob("**/SKILL.md"):
        content = skill_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            continue

        try:
            # Simple frontmatter parser
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            frontmatter_raw = parts[1]
            body = parts[2]

            data = yaml.safe_load(frontmatter_raw) or {}

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
                skill_file.write_text(new_content, encoding="utf-8")
                print(f"Fixed skill: {skill_file}")

        except Exception as e:
            print(f"Error processing {skill_file}: {e}")

def fix_workflows():
    wf_dir = AGENT_DIR / "workflows"
    if not wf_dir.exists():
        return

    for wf_file in wf_dir.glob("*.md"):
        content = wf_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            # Add frontmatter if missing entirely
            new_content = f"---\nlcm_state: beta\nversion: \"1.0\"\n---\n\n{content}"
            wf_file.write_text(new_content, encoding="utf-8")
            print(f"Added frontmatter to workflow: {wf_file}")
            continue

        try:
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            frontmatter_raw = parts[1]
            body = parts[2]

            data = yaml.safe_load(frontmatter_raw) or {}

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
                wf_file.write_text(new_content, encoding="utf-8")
                print(f"Fixed workflow: {wf_file}")

        except Exception as e:
            print(f"Error processing {wf_file}: {e}")

if __name__ == "__main__":
    fix_skills()
    fix_workflows()
