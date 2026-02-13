import re
import os

FILES = [
    "mekhane/anamnesis/session_indexer.py",
    "mekhane/synteleia/dokimasia/multi_semantic_agent.py",
    "mekhane/synteleia/dokimasia/ochema_backend.py",
    "mekhane/ochema/antigravity_client.py",
    "mekhane/ochema/__init__.py",
    "mekhane/ochema/cli.py",
]

# Regex to find def/class, handling indent and optional decorators
# Matches: indent, decorators, def/class, name
DEF_RE = re.compile(r"^(\s*)((?:@.+\n\s*)*)(?:async\s+)?(def|class)\s+([a-zA-Z0-9_]+)")

def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line is a definition start (including decorators)
        # We need to look ahead/context, but regex is per line usually.
        # Let's use a simpler approach: process line by line, but if we see a def/class,
        # we check backwards for decorators and PURPOSE.

        # Actually, let's just look for "def " or "class "
        match = re.match(r"^(\s*)(?:async\s+)?(def|class)\s+([a-zA-Z0-9_]+)", line)
        if match:
            indent = match.group(1)
            kind = match.group(2)
            name = match.group(3)

            # Look back for decorators
            j = len(new_lines) - 1
            has_purpose = False
            insert_pos = len(new_lines) # Default insert before def

            # Walk back through decorators
            while j >= 0:
                prev = new_lines[j]
                if re.match(r"^\s*@", prev):
                    insert_pos = j
                    j -= 1
                elif re.match(r"^\s*#\s*PURPOSE:", prev):
                    has_purpose = True
                    break
                else:
                    break # Not a decorator or purpose

            if not has_purpose:
                # Insert PURPOSE
                purpose_line = f"{indent}# PURPOSE: {name.replace('_', ' ').capitalize()}\n"
                new_lines.insert(insert_pos, purpose_line)

        new_lines.append(line)
        i += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Fixed {filepath}")

for f in FILES:
    if os.path.exists(f):
        fix_file(f)
    else:
        print(f"Skipping {f} (not found)")
