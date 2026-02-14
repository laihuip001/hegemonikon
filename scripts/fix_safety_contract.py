
import os
from pathlib import Path
import yaml

AGENT_DIR = Path(".agent")

def fix_skills():
    skills_dir = AGENT_DIR / "skills"
    if not skills_dir.exists():
        return

    for skill_md in skills_dir.rglob("SKILL.md"):
        if "TEMPLATE" in skill_md.name.upper() or "_archive" in skill_md.parts:
            continue

        try:
            content = skill_md.read_text(encoding="utf-8")
            if content.startswith("---"):
                # Already has frontmatter, parse it
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    fm_str = parts[1]
                    body = parts[2]
                    try:
                        fm = yaml.safe_load(fm_str) or {}
                        updated = False
                        if "risk_tier" not in fm:
                            fm["risk_tier"] = "L1"
                            updated = True
                        if "risks" not in fm:
                            fm["risks"] = ["unknown"]
                            updated = True

                        if updated:
                            new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False).strip()
                            new_content = f"---\n{new_fm}\n---{body}"
                            skill_md.write_text(new_content, encoding="utf-8")
                            print(f"Fixed {skill_md}")
                    except Exception as e:
                        print(f"Failed to parse FM in {skill_md}: {e}")
            else:
                # No frontmatter, add it
                fm = {"risk_tier": "L1", "risks": ["unknown"]}
                new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False).strip()
                new_content = f"---\n{new_fm}\n---\n\n{content}"
                skill_md.write_text(new_content, encoding="utf-8")
                print(f"Added FM to {skill_md}")
        except Exception as e:
            print(f"Error processing {skill_md}: {e}")

def fix_workflows():
    wf_dir = AGENT_DIR / "workflows"
    if not wf_dir.exists():
        return

    for wf_md in wf_dir.glob("*.md"):
        try:
            content = wf_md.read_text(encoding="utf-8")
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    fm_str = parts[1]
                    body = parts[2]
                    try:
                        fm = yaml.safe_load(fm_str) or {}
                        updated = False
                        if "lcm_state" not in fm:
                            fm["lcm_state"] = "beta"
                            updated = True
                        if "version" not in fm:
                            fm["version"] = "1.0.0"
                            updated = True

                        if updated:
                            new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False).strip()
                            new_content = f"---\n{new_fm}\n---{body}"
                            wf_md.write_text(new_content, encoding="utf-8")
                            print(f"Fixed {wf_md}")
                    except Exception as e:
                        print(f"Failed to parse FM in {wf_md}: {e}")
            else:
                fm = {"lcm_state": "beta", "version": "1.0.0"}
                new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False).strip()
                new_content = f"---\n{new_fm}\n---\n\n{content}"
                wf_md.write_text(new_content, encoding="utf-8")
                print(f"Added FM to {wf_md}")
        except Exception as e:
            print(f"Error processing {wf_md}: {e}")

if __name__ == "__main__":
    fix_skills()
    fix_workflows()
