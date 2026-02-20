import os

def fix_file(filepath):
    filepath = filepath.strip()
    if not filepath or not os.path.exists(filepath):
        return

    with open(filepath, 'r') as f:
        lines = f.readlines()

    if len(lines) >= 2:
        # Check if first line is PROOF and second is shebang
        if lines[0].startswith("# PROOF:") and lines[1].startswith("#!"):
            print(f"Fixing {filepath}")
            lines[0], lines[1] = lines[1], lines[0]
            with open(filepath, 'w') as f:
                f.writelines(lines)

with open('candidates.txt', 'r') as f:
    for line in f:
        fix_file(line)
