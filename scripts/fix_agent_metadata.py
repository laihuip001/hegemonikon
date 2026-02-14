#!/usr/bin/env python3
# PURPOSE: Automate fixing missing metadata in agent skills and workflows
"""
Fix Agent Metadata

Adds missing frontmatter fields required by the Dendron Safety Contract:
- Skills: risk_tier, risks
- Workflows: lcm_state, version

Usage:
    python scripts/fix_agent_metadata.py
"""

import os
from pathlib import Path
import yaml

AGENT_DIR = Path(".agent")

def fix_skill(path: Path):
    content = path.read_text(encoding="utf-8")
    if content.startswith("---"):
        try:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm = yaml.safe_load(parts[1]) or {}
                changed = False
                if "risk_tier" not in fm:
                    fm["risk_tier"] = "L1"
                    changed = True
                if "risks" not in fm:
                    fm["risks"] = []
                    changed = True

                if changed:
                    new_fm = yaml.dump(fm, default_flow_style=None, sort_keys=False).strip()
                    new_content = f"---\n{new_fm}\n---{parts[2]}"
                    path.write_text(new_content, encoding="utf-8")
                    print(f"Fixed skill: {path}")
                    return
        except Exception as e:
            print(f"Error parsing {path}: {e}")

def fix_workflow(path: Path):
    content = path.read_text(encoding="utf-8")
    if content.startswith("---"):
        try:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm = yaml.safe_load(parts[1]) or {}
                changed = False
                if "lcm_state" not in fm:
                    fm["lcm_state"] = "beta"
                    changed = True
                if "version" not in fm:
                    fm["version"] = "1.0"
                    changed = True

                if changed:
                    new_fm = yaml.dump(fm, default_flow_style=None, sort_keys=False).strip()
                    new_content = f"---\n{new_fm}\n---{parts[2]}"
                    path.write_text(new_content, encoding="utf-8")
                    print(f"Fixed workflow: {path}")
                    return
        except Exception as e:
            print(f"Error parsing {path}: {e}")

def main():
    if not AGENT_DIR.exists():
        print(f"Agent dir not found: {AGENT_DIR}")
        return

    # Skills
    skills_dir = AGENT_DIR / "skills"
    if skills_dir.exists():
        for f in skills_dir.glob("**/SKILL.md"):
            fix_skill(f)

    # Workflows
    wf_dir = AGENT_DIR / "workflows"
    if wf_dir.exists():
        for f in wf_dir.glob("*.md"):
            fix_workflow(f)

if __name__ == "__main__":
    main()
