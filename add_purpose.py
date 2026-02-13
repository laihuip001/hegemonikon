import re
import sys
from pathlib import Path

def process_file(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return

    lines = path.read_text(encoding="utf-8").splitlines()
    new_lines = []

    # Regex to match def/class with indentation
    # Group 1: Indentation
    # Group 2: Type (def/class)
    # Group 3: Name
    pattern = re.compile(r"^(\s*)(def|class)\s+([a-zA-Z0-9_]+)")

    for i, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            indent = match.group(1)
            name = match.group(3)

            # Check if previous line is a PURPOSE comment
            # We look at new_lines[-1] if it exists
            has_purpose = False
            if new_lines:
                last_line = new_lines[-1].strip()
                if last_line.startswith("# PURPOSE:"):
                    has_purpose = True

            # Also check if it's a decorator line, we might need to go back further
            # But strictly speaking, Dendron usually expects PURPOSE before decorators or def.
            # Let's simple check: if we are about to write def/class, check if we just wrote PURPOSE.

            if not has_purpose:
                # Add PURPOSE comment with same indentation
                # Use a slightly better description than just the name
                description = f"Define {name}"
                new_lines.append(f"{indent}# PURPOSE: {description}")

        new_lines.append(line)

    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"Processed {filepath}")

if __name__ == "__main__":
    for f in sys.argv[1:]:
        process_file(f)
