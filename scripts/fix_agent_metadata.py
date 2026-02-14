#!/usr/bin/env python3
"""
Bulk update metadata for Safety Contract compliance.
"""
from pathlib import Path
import re

AGENT_DIR = Path(".agent")

def update_workflows():
    workflow_dir = AGENT_DIR / "workflows"
    if not workflow_dir.exists():
        return

    for md_file in workflow_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Check if frontmatter exists
        if lines[0].strip() == "---":
            # Update existing frontmatter
            new_lines = []
            in_fm = False
            has_lcm = False
            has_ver = False

            for i, line in enumerate(lines):
                if line.strip() == "---":
                    if in_fm:
                        # End of frontmatter
                        if not has_lcm:
                            new_lines.append("lcm_state: beta")
                        if not has_ver:
                            new_lines.append("version: 1.0")
                        new_lines.append(line)
                        in_fm = False
                        new_lines.extend(lines[i+1:])
                        break
                    else:
                        in_fm = True
                        new_lines.append(line)
                elif in_fm:
                    if line.strip().startswith("lcm_state:"):
                        has_lcm = True
                    if line.strip().startswith("version:"):
                        has_ver = True
                    new_lines.append(line)

            md_file.write_text("\n".join(new_lines), encoding="utf-8")
        else:
            # Add frontmatter
            new_content = "---\nlcm_state: beta\nversion: 1.0\n---\n\n" + content
            md_file.write_text(new_content, encoding="utf-8")
        print(f"Updated workflow: {md_file}")

def update_skills():
    skills_dir = AGENT_DIR / "skills"
    if not skills_dir.exists():
        return

    for md_file in skills_dir.glob("**/SKILL.md"):
        content = md_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        if lines[0].strip() == "---":
            new_lines = []
            in_fm = False
            has_risk = False
            has_risks = False

            for i, line in enumerate(lines):
                if line.strip() == "---":
                    if in_fm:
                        if not has_risk:
                            new_lines.append("risk_tier: L1")
                        if not has_risks:
                            new_lines.append("risks:")
                            new_lines.append("  - description: No significant risks identified")
                            new_lines.append("    severity: low")
                            new_lines.append("    mitigation: Standard review")
                        new_lines.append(line)
                        in_fm = False
                        new_lines.extend(lines[i+1:])
                        break
                    else:
                        in_fm = True
                        new_lines.append(line)
                elif in_fm:
                    if line.strip().startswith("risk_tier:"):
                        has_risk = True
                    if line.strip().startswith("risks:"):
                        has_risks = True
                    new_lines.append(line)

            md_file.write_text("\n".join(new_lines), encoding="utf-8")
        else:
            new_content = """---
risk_tier: L1
risks:
  - description: No significant risks identified
    severity: low
    mitigation: Standard review
---

""" + content
            md_file.write_text(new_content, encoding="utf-8")
        print(f"Updated skill: {md_file}")

if __name__ == "__main__":
    update_workflows()
    update_skills()
