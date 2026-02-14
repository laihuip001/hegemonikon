import os
import yaml
from pathlib import Path

AGENT_DIR = Path(".agent")

def fix_metadata():
    if not AGENT_DIR.exists():
        print(f"Directory {AGENT_DIR} not found.")
        return

    # Fix Skills
    skills_dir = AGENT_DIR / "skills"
    if skills_dir.exists():
        for skill_file in skills_dir.glob("**/SKILL.md"):
            fix_frontmatter(skill_file, {"risk_tier": "L1", "risks": ["none"]})

    # Fix Workflows
    workflows_dir = AGENT_DIR / "workflows"
    if workflows_dir.exists():
        for wf_file in workflows_dir.glob("*.md"):
            fix_frontmatter(wf_file, {"lcm_state": "beta", "version": "1.0"})

def fix_frontmatter(filepath: Path, defaults: dict):
    try:
        content = filepath.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return # No frontmatter, skip or handle differently

        parts = content.split("---", 2)
        if len(parts) < 3:
            return

        frontmatter_raw = parts[1]
        body = parts[2]

        try:
            data = yaml.safe_load(frontmatter_raw) or {}
        except yaml.YAMLError:
            return

        changed = False
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
                changed = True

        if changed:
            new_frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False).strip()
            new_content = f"---\n{new_frontmatter}\n---{body}"
            filepath.write_text(new_content, encoding="utf-8")
            print(f"Fixed {filepath}")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    fix_metadata()
