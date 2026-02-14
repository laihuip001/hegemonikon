import os
import yaml
from pathlib import Path

AGENT_ROOT = Path(".agent")
WORKFLOWS_DIR = AGENT_ROOT / "workflows"
SKILLS_DIR = AGENT_ROOT / "skills"

def add_metadata(path, updates):
    try:
        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            # Update existing frontmatter
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                    changed = False
                    for k, v in updates.items():
                        if k not in fm:
                            fm[k] = v
                            changed = True
                    if changed:
                        new_fm = yaml.dump(fm, default_flow_style=False).strip()
                        new_content = f"---\n{new_fm}\n---{parts[2]}"
                        path.write_text(new_content, encoding="utf-8")
                        print(f"Updated {path}")
                except Exception as e:
                    print(f"Error parsing frontmatter in {path}: {e}")
        else:
            # Add new frontmatter
            fm = yaml.dump(updates, default_flow_style=False).strip()
            new_content = f"---\n{fm}\n---\n\n{content}"
            path.write_text(new_content, encoding="utf-8")
            print(f"Created frontmatter in {path}")
    except Exception as e:
        print(f"Error processing {path}: {e}")

# Fix Workflows: lcm_state, version
if WORKFLOWS_DIR.exists():
    for f in WORKFLOWS_DIR.glob("*.md"):
        add_metadata(f, {"lcm_state": "beta", "version": "1.0.0"})

# Fix Skills: risk_tier, risks
if SKILLS_DIR.exists():
    for f in SKILLS_DIR.rglob("*.md"):
        if f.name == "SKILL.md":
            add_metadata(f, {"risk_tier": "L1", "risks": ["general_execution_risk"]})
