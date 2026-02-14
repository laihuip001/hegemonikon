import os
import re

files = [
    ".agent/skills/category-engine/SKILL.md",
    ".agent/skills/agora/SKILL.md"
]

for filepath in files:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue

    with open(filepath, "r") as f:
        content = f.read()

    # Split frontmatter
    # YAML frontmatter is between first two ---
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if not match:
        print(f"No frontmatter found in {filepath}")
        continue

    frontmatter = match.group(1)
    body = match.group(2)

    # Check if metadata already in frontmatter
    if "risk_tier:" in frontmatter and "risks:" in frontmatter:
        print(f"Metadata already in frontmatter for {filepath}")
    else:
        # Append to frontmatter
        if "risk_tier:" not in frontmatter:
            frontmatter += "\nrisk_tier: L1"
        if "risks:" not in frontmatter:
            frontmatter += "\nrisks: 中程度の解釈的誤り"
        print(f"Added metadata to frontmatter for {filepath}")

    # Remove metadata from body if present
    # Pattern: \nrisk_tier: L1\nrisks: ... at the end
    body = re.sub(r"\nrisk_tier: L1\nrisks: .*?\n?", "", body, flags=re.DOTALL)
    body = re.sub(r"\nrisk_tier: L1\nrisks: .*?$", "", body, flags=re.DOTALL) # In case no trailing newline

    # Reconstruct file
    new_content = f"---\n{frontmatter}\n---\n{body}"

    with open(filepath, "w") as f:
        f.write(new_content)

    print(f"Fixed {filepath}")
