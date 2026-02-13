
import sys
import re
from pathlib import Path

def add_purpose_comments(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return

    lines = path.read_text().splitlines()
    new_lines = []

    # Regex to find function definitions
    # Matches "def func_name" with indentation
    def_pattern = re.compile(r'^(\s*)def\s+([a-zA-Z0-9_]+)\s*\(')

    # Check if the previous line is a comment (simplified check)
    comment_pattern = re.compile(r'^\s*#.*')
    purpose_pattern = re.compile(r'^\s*#\s*PURPOSE:', re.IGNORECASE)

    for i, line in enumerate(lines):
        match = def_pattern.match(line)
        if match:
            indent = match.group(1)
            func_name = match.group(2)

            # Check previous line
            prev_line_idx = len(new_lines) - 1
            has_purpose = False

            # Scan backwards for existing comments/decorators
            j = prev_line_idx
            while j >= 0:
                prev_line = new_lines[j]
                if purpose_pattern.match(prev_line):
                    has_purpose = True
                    break
                elif prev_line.strip().startswith('@') or prev_line.strip().startswith('#'):
                    # Skip decorators and other comments
                    j -= 1
                else:
                    # Found something else (blank line, code), stop looking
                    break

            if not has_purpose:
                # Add PURPOSE comment
                # Humanize function name: split by underscore, capitalize
                human_name = ' '.join(word.capitalize() for word in func_name.split('_'))
                purpose_comment = f"{indent}# PURPOSE: {human_name}"

                # If there are decorators, insert before them
                insert_idx = len(new_lines)
                while insert_idx > 0 and (new_lines[insert_idx-1].strip().startswith('@')):
                    insert_idx -= 1

                new_lines.insert(insert_idx, purpose_comment)
                print(f"Added PURPOSE to {func_name} in {filepath}")

        new_lines.append(line)

    path.write_text('\n'.join(new_lines) + '\n')

if __name__ == "__main__":
    for f in sys.argv[1:]:
        add_purpose_comments(f)
