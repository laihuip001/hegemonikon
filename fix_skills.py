import os
import re

files = [
    ".agent/skills/antigravity-expert/SKILL.md",
    ".agent/skills/dendron/SKILL.md",
    ".agent/skills/fep-engine/SKILL.md",
    ".agent/skills/hermeneus-dispatch/SKILL.md",
    ".agent/skills/peira/SKILL.md",
    ".agent/skills/poiema/SKILL.md",
    ".agent/skills/synedrion/SKILL.md",
    ".agent/skills/synteleia/SKILL.md",
    ".agent/skills/taxis/SKILL.md",
]

fields_to_add = """
risk_tier: L1
reversible: true
requires_approval: false
risks: []
fallbacks: []
"""

for filepath in files:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the end of the frontmatter (second '---')
    parts = content.split("---", 2)
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = parts[2]

        # Check if fields already exist (simple check)
        if "risk_tier:" not in frontmatter:
            new_frontmatter = frontmatter.rstrip() + fields_to_add
            new_content = "---" + new_frontmatter + "\n---" + body

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {filepath}")
        else:
            print(f"Skipped {filepath} (fields likely present)")
    else:
        print(f"Could not parse frontmatter in {filepath}")
