#!/usr/bin/env python3
# PURPOSE: Fix missing metadata in .agent/ skills and workflows
"""
Fix Agent Metadata

Scans .agent/skills/ and .agent/workflows/ for missing frontmatter fields required by
the Dendron Safety Contract check.

Target fields:
- Skills: risk_tier, risks
- Workflows: lcm_state, version
"""

import sys
from pathlib import Path

# Fix for missing mekhane package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def fix_skills(agent_dir: Path):
    skills_dir = agent_dir / "skills"
    if not skills_dir.exists():
        print(f"Skipping skills (not found): {skills_dir}")
        return

    fixed_count = 0
    for skill_file in skills_dir.glob("**/SKILL.md"):
        try:
            content = skill_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            if not lines or lines[0].strip() != "---":
                continue

            # Find frontmatter end
            end_idx = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    end_idx = i
                    break

            if end_idx == -1:
                continue

            frontmatter = lines[1:end_idx]
            has_risk_tier = any(l.strip().startswith("risk_tier:") for l in frontmatter)
            has_risks = any(l.strip().startswith("risks:") for l in frontmatter)

            new_frontmatter = list(frontmatter)
            modified = False

            if not has_risk_tier:
                new_frontmatter.append("risk_tier: L1")
                modified = True

            if not has_risks:
                new_frontmatter.append("risks:")
                new_frontmatter.append("  - none")
                modified = True

            if modified:
                new_content = "---\n" + "\n".join(new_frontmatter) + "\n" + "\n".join(lines[end_idx:])
                skill_file.write_text(new_content, encoding="utf-8")
                fixed_count += 1
                print(f"Fixed skill: {skill_file.relative_to(agent_dir)}")

        except Exception as e:
            print(f"Error fixing skill {skill_file}: {e}")

    print(f"Skills fixed: {fixed_count}")


def fix_workflows(agent_dir: Path):
    workflows_dir = agent_dir / "workflows"
    if not workflows_dir.exists():
        print(f"Skipping workflows (not found): {workflows_dir}")
        return

    fixed_count = 0
    for wf_file in workflows_dir.glob("*.md"):
        try:
            content = wf_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            if not lines or lines[0].strip() != "---":
                continue

            # Find frontmatter end
            end_idx = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    end_idx = i
                    break

            if end_idx == -1:
                continue

            frontmatter = lines[1:end_idx]
            has_lcm = any(l.strip().startswith("lcm_state:") for l in frontmatter)
            has_version = any(l.strip().startswith("version:") for l in frontmatter)

            new_frontmatter = list(frontmatter)
            modified = False

            if not has_lcm:
                new_frontmatter.append("lcm_state: beta")
                modified = True

            if not has_version:
                new_frontmatter.append("version: 1.0.0")
                modified = True

            if modified:
                new_content = "---\n" + "\n".join(new_frontmatter) + "\n" + "\n".join(lines[end_idx:])
                wf_file.write_text(new_content, encoding="utf-8")
                fixed_count += 1
                print(f"Fixed workflow: {wf_file.relative_to(agent_dir)}")

        except Exception as e:
            print(f"Error fixing workflow {wf_file}: {e}")

    print(f"Workflows fixed: {fixed_count}")


if __name__ == "__main__":
    agent_dir = Path(".agent")
    if not agent_dir.exists():
        print(f"Error: .agent directory not found in {Path.cwd()}")
        sys.exit(1)

    print("Fixing Agent Metadata...")
    fix_skills(agent_dir)
    fix_workflows(agent_dir)
    print("Done.")
