#!/usr/bin/env python3
"""
Fix Proof Headers Script

Iterates through directories and injects missing # PROOF: headers into Python files.
Standard format: # PROOF: [L2/Mekhane] <- {parent}/ A0->Auto->AddedByCI
"""

import os
from pathlib import Path

TARGET_DIR = Path("mekhane")
PROOF_TEMPLATE = "# PROOF: [L2/Mekhane] <- {parent}/ A0->Auto->AddedByCI"

def fix_file(filepath: Path):
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check if PROOF header exists
        has_proof = any(line.startswith("# PROOF:") for line in lines)
        if has_proof:
            return

        # Determine insertion point (after shebang)
        insert_idx = 0
        if lines and lines[0].startswith("#!"):
            insert_idx = 1

        parent_dir = filepath.parent.name
        header = PROOF_TEMPLATE.format(parent=parent_dir)

        lines.insert(insert_idx, header)
        filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Fixed: {filepath}")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    if not TARGET_DIR.exists():
        print(f"Directory {TARGET_DIR} not found.")
        return

    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".py"):
                fix_file(Path(root) / file)

if __name__ == "__main__":
    main()
