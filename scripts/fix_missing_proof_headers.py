#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/fix_missing_proof_headers.py A3→Maintenance→AutoFix
# PURPOSE: Batch add missing PROOF headers to Python files
"""
Batch adds missing PROOF headers to Python files.
"""
import sys
from pathlib import Path

def fix_file(path: Path):
    try:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check if PROOF already exists
        if any(line.startswith("# PROOF:") for line in lines):
            return

        # Determine category
        category = "[L2/Mekhane]"
        if "dendron" in str(path):
            category = "[L2/Quality]"
        elif "symploke" in str(path):
            category = "[L2/Infra]"
        elif "basanos" in str(path):
            category = "[L2/Test]"
        elif "periskope" in str(path):
            category = "[L2/Search]"
        elif "api" in str(path):
            category = "[L3/API]"

        parent = str(path.parent) + "/"
        proof_line = f"# PROOF: {category} <- {parent} Auto-generated existence proof"

        new_lines = []
        inserted = False

        # Insert after shebang if exists
        if lines and lines[0].startswith("#!"):
            new_lines.append(lines[0])
            new_lines.append(proof_line)
            new_lines.extend(lines[1:])
            inserted = True
        else:
            new_lines.append(proof_line)
            new_lines.extend(lines)
            inserted = True

        if inserted:
            path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            print(f"Fixed: {path}")

    except Exception as e:
        print(f"Error fixing {path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_missing_proof_headers.py <file1> <file2> ...")
        sys.exit(1)

    for arg in sys.argv[1:]:
        fix_file(Path(arg))
