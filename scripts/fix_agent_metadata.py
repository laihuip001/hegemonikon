#!/usr/bin/env python3
# PURPOSE: Fix missing metadata in .agent/skills and .agent/workflows to pass Dendron Safety Contract
"""
Fix Agent Metadata

Adds default metadata to SKILL.md and workflow/*.md files to satisfy
mekhane.dendron.cli skill-audit checks.

Defaults:
- Skills: risk_tier: L1, risks: []
- Workflows: lcm_state: beta, version: 1.0
"""

import sys
from pathlib import Path
import yaml

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Run 'pip install pyyaml'.")
    sys.exit(1)

def fix_skills(root: Path):
    """Fix missing metadata in SKILL.md files."""
    skills_dir = root / ".agent" / "skills"
    if not skills_dir.exists():
        print(f"Skipping skills (not found): {skills_dir}")
        return

    print(f"Scanning skills in {skills_dir}...")
    count = 0
    fixed = 0

    for path in skills_dir.rglob("SKILL.md"):
        count += 1
        try:
            content = path.read_text(encoding="utf-8")
            parts = content.split("---", 2)

            if len(parts) >= 3 and parts[0].strip() == "":
                # Has frontmatter
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    print(f"  ⚠️ Invalid YAML in {path}")
                    continue

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
                    print(f"  ✅ Fixed: {path.relative_to(root)}")
                    fixed += 1
            else:
                # No frontmatter
                default_fm = "risk_tier: L1\nrisks: []"
                new_content = f"---\n{default_fm}\n---\n\n{content}"
                path.write_text(new_content, encoding="utf-8")
                print(f"  ✅ Added frontmatter: {path.relative_to(root)}")
                fixed += 1

        except Exception as e:
            print(f"  ❌ Error processing {path}: {e}")

    print(f"Skills: Scanned {count}, Fixed {fixed}")


def fix_workflows(root: Path):
    """Fix missing metadata in workflow markdown files."""
    wf_dir = root / ".agent" / "workflows"
    if not wf_dir.exists():
        print(f"Skipping workflows (not found): {wf_dir}")
        return

    print(f"Scanning workflows in {wf_dir}...")
    count = 0
    fixed = 0

    for path in wf_dir.glob("*.md"):
        count += 1
        try:
            content = path.read_text(encoding="utf-8")
            parts = content.split("---", 2)

            if len(parts) >= 3 and parts[0].strip() == "":
                # Has frontmatter
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    print(f"  ⚠️ Invalid YAML in {path}")
                    continue

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
                    print(f"  ✅ Fixed: {path.relative_to(root)}")
                    fixed += 1
            else:
                # No frontmatter
                default_fm = "lcm_state: beta\nversion: '1.0'"
                new_content = f"---\n{default_fm}\n---\n\n{content}"
                path.write_text(new_content, encoding="utf-8")
                print(f"  ✅ Added frontmatter: {path.relative_to(root)}")
                fixed += 1

        except Exception as e:
            print(f"  ❌ Error processing {path}: {e}")

    print(f"Workflows: Scanned {count}, Fixed {fixed}")


if __name__ == "__main__":
    root = Path.cwd()
    fix_skills(root)
    fix_workflows(root)
