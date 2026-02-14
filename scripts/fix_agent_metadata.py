#!/usr/bin/env python3
# PROOF: [L2/Infra] <- scripts/ Agent Metadata Fixer
"""
Fix Agent Metadata — Dendron Safety Contract Auditor

Bulk updates .agent/skills and .agent/workflows to add missing mandatory metadata fields
required by the Dendron skill-audit check.

Missing fields handled:
- Skills: risk_tier (default: L1), risks (default: [])
- Workflows: lcm_state (default: beta), version (default: "1.0")

Usage:
    python scripts/fix_agent_metadata.py
"""

import sys
from pathlib import Path
import yaml

def fix_skills(agent_dir: Path):
    """Fix missing metadata in skill markdown files."""
    skills_dir = agent_dir / "skills"
    if not skills_dir.exists():
        return

    print(f"Checking skills in {skills_dir}...")
    count = 0
    for md_file in skills_dir.rglob("*.md"):
        if md_file.name in ("README.md", "PROOF.md"):
            continue

        content = md_file.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            continue

        try:
            # Extract frontmatter
            parts = content.split("---\n", 2)
            if len(parts) < 3:
                continue

            frontmatter_raw = parts[1]
            body = parts[2]

            # Load YAML
            data = yaml.safe_load(frontmatter_raw) or {}

            updated = False
            if "risk_tier" not in data:
                data["risk_tier"] = "L1"
                updated = True
            if "risks" not in data:
                data["risks"] = []
                updated = True

            if updated:
                # Dump YAML preserving some formatting if possible, but safe_dump is safer
                new_fm = yaml.safe_dump(data, default_flow_style=None, sort_keys=False, allow_unicode=True).strip()
                new_content = f"---\n{new_fm}\n---\n{body}"
                md_file.write_text(new_content, encoding="utf-8")
                print(f"  Fixed: {md_file.relative_to(agent_dir)}")
                count += 1

        except Exception as e:
            print(f"  Error processing {md_file.name}: {e}")

    print(f"Fixed {count} skills.")

def fix_workflows(agent_dir: Path):
    """Fix missing metadata in workflow markdown files."""
    wf_dir = agent_dir / "workflows"
    if not wf_dir.exists():
        return

    print(f"Checking workflows in {wf_dir}...")
    count = 0
    for md_file in wf_dir.glob("*.md"):
        if md_file.name in ("README.md", "PROOF.md"):
            continue

        content = md_file.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            continue

        try:
            parts = content.split("---\n", 2)
            if len(parts) < 3:
                continue

            frontmatter_raw = parts[1]
            body = parts[2]

            data = yaml.safe_load(frontmatter_raw) or {}

            updated = False
            if "lcm_state" not in data:
                data["lcm_state"] = "beta"
                updated = True
            if "version" not in data:
                data["version"] = "1.0"
                updated = True

            if updated:
                new_fm = yaml.safe_dump(data, default_flow_style=None, sort_keys=False, allow_unicode=True).strip()
                new_content = f"---\n{new_fm}\n---\n{body}"
                md_file.write_text(new_content, encoding="utf-8")
                print(f"  Fixed: {md_file.relative_to(agent_dir)}")
                count += 1

        except Exception as e:
            print(f"  Error processing {md_file.name}: {e}")

    print(f"Fixed {count} workflows.")

def main():
    root = Path(__file__).resolve().parent.parent
    agent_dir = root / ".agent"

    if not agent_dir.exists():
        print(f"Error: .agent directory not found at {agent_dir}")
        sys.exit(1)

    fix_skills(agent_dir)
    fix_workflows(agent_dir)

if __name__ == "__main__":
    main()
