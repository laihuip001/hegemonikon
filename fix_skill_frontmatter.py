
import sys
from pathlib import Path

def fix_frontmatter(filepath):
    path = Path(filepath)
    if not path.exists():
        return

    content = path.read_text()
    lines = content.splitlines()

    if not lines or lines[0].strip() != '---':
        print(f"Skipping {filepath}: No frontmatter start found")
        return

    # Find the end of the first frontmatter block
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        print(f"Skipping {filepath}: No frontmatter end found")
        return

    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = '\n'.join(frontmatter_lines)

    required_fields = {
        'risk_tier': 'L1',
        'risks': '[]',
        'reversible': 'true',
        'requires_approval': 'false',
        'fallbacks': '[]'
    }

    new_fields = []
    for key, value in required_fields.items():
        if f"{key}:" not in frontmatter_text:
            new_fields.append(f"{key}: {value}")

    if new_fields:
        # Insert new fields before the end of the frontmatter
        for field in reversed(new_fields):
            lines.insert(end_idx, field)

        path.write_text('\n'.join(lines) + '\n')
        print(f"Fixed {filepath}")
    else:
        print(f"Skipping {filepath}: All fields present")

if __name__ == "__main__":
    for f in sys.argv[1:]:
        fix_frontmatter(f)
