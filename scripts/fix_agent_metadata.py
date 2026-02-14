import os
from pathlib import Path

AGENT_DIR = Path(".agent")

def fix_skills():
    for skill_file in AGENT_DIR.glob("skills/**/SKILL.md"):
        content = skill_file.read_text(encoding="utf-8")
        if "risk_tier:" not in content:
            print(f"Fixing {skill_file}")
            # Insert after the first ---
            lines = content.split("\n")
            if lines[0].strip() == "---":
                # Find end of frontmatter
                try:
                    end_idx = lines.index("---", 1)
                    lines.insert(end_idx, "risk_tier: L1")
                    lines.insert(end_idx + 1, "risks:")
                    lines.insert(end_idx + 2, "  - none")
                    skill_file.write_text("\n".join(lines), encoding="utf-8")
                except ValueError:
                    print(f"Skipping {skill_file} (no frontmatter)")

def fix_workflows():
    for wf_file in AGENT_DIR.glob("workflows/*.md"):
        content = wf_file.read_text(encoding="utf-8")
        lines = content.split("\n")
        updated = False
        if "lcm_state:" not in content and lines[0].strip() == "---":
            try:
                end_idx = lines.index("---", 1)
                lines.insert(end_idx, "lcm_state: beta")
                updated = True
            except ValueError:
                pass

        if "version:" not in content and lines[0].strip() == "---":
            try:
                end_idx = lines.index("---", 1)
                if not updated: # Find index again if not updated yet, or reuse if we inserted lines?
                     # Actually, if we inserted, the index shifted. Better to re-find or insert at top.
                     pass
                # Simpler approach: reconstruct
                pass
            except ValueError:
                pass

        if updated:
             # This loop logic is a bit fragile. Let's restart for version.
             pass

    # Robust pass
    for wf_file in AGENT_DIR.glob("workflows/*.md"):
        content = wf_file.read_text(encoding="utf-8")
        if "lcm_state:" in content and "version:" in content:
            continue

        lines = content.split("\n")
        if lines[0].strip() != "---":
            continue

        try:
            end_idx = lines.index("---", 1)
            inserts = []
            if "lcm_state:" not in content:
                inserts.append("lcm_state: beta")
            if "version:" not in content:
                inserts.append("version: 1.0.0")

            if inserts:
                print(f"Fixing {wf_file}")
                for ins in reversed(inserts):
                    lines.insert(end_idx, ins)
                wf_file.write_text("\n".join(lines), encoding="utf-8")
        except ValueError:
            pass

if __name__ == "__main__":
    fix_skills()
    fix_workflows()
