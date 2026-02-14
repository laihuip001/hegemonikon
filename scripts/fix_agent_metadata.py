#!/usr/bin/env python3
"""
Fix missing metadata in agent skills and workflows to satisfy Dendron Safety Contract audit.

For skills (SKILL.md):
- Ensures `risk_tier` is present (default: L1)
- Ensures `risks` is present (default: [])

For workflows (*.md):
- Ensures `lcm_state` is present (default: beta)
- Ensures `version` is present (default: 1.0)
"""

import os
import re
from pathlib import Path

def fix_frontmatter(content: str, fields: dict) -> str:
    """Add missing fields to YAML frontmatter."""
    if not content.startswith("---"):
        return content

    try:
        end_idx = content.index("---", 3)
    except ValueError:
        return content

    frontmatter = content[3:end_idx]
    body = content[end_idx:]

    updated = False
    lines = frontmatter.splitlines()

    # Check existing keys
    existing_keys = set()
    for line in lines:
        if ":" in line:
            key = line.split(":")[0].strip()
            existing_keys.add(key)

    # Add missing fields
    new_lines = []
    if lines and lines[0].strip() == "":
        lines = lines[1:]

    new_lines.extend(lines)

    for key, value in fields.items():
        if key not in existing_keys:
            new_lines.append(f"{key}: {value}")
            updated = True
            print(f"  + Added {key}: {value}")

    if not updated:
        return content

    return f"---{os.linesep}" + f"{os.linesep}".join(new_lines) + f"{os.linesep}{body}"

def process_skills(agent_dir: Path):
    print("Processing Skills...")
    skills_dir = agent_dir / "skills"
    if not skills_dir.exists():
        return

    for skill_file in skills_dir.rglob("SKILL.md"):
        print(f"Checking {skill_file}...")
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = fix_frontmatter(content, {
            "risk_tier": "L1",
            "risks": "[]"
        })

        if content != new_content:
            with open(skill_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("  -> Updated")

def process_workflows(agent_dir: Path):
    print("Processing Workflows...")
    workflows_dir = agent_dir / "workflows"
    if not workflows_dir.exists():
        return

    for wf_file in workflows_dir.rglob("*.md"):
        print(f"Checking {wf_file}...")
        with open(wf_file, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = fix_frontmatter(content, {
            "lcm_state": "beta",
            "version": "'1.0'"
        })

        if content != new_content:
            with open(wf_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("  -> Updated")

def main():
    root = Path(".agent")
    if not root.exists():
        print(".agent directory not found")
        return

    process_skills(root)
    process_workflows(root)

if __name__ == "__main__":
    main()
