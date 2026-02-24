#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/ A0->Auto->AddedByCI
# PURPOSE: mekhane/ 以下の Python ファイルに PROOF ヘッダを一括注入する
"""
Fix missing PROOF headers in mekhane/ directory.

Iterates through all .py files in mekhane/ and injects a default PROOF header
if one is missing. Preserves shebang lines.
"""

import sys
from pathlib import Path

# Target directory
TARGET_DIR = Path("mekhane")

# Default PROOF header format
# [Level/Category] <- path/to/source Axiom->Reason->Module
PROOF_TEMPLATE = "# PROOF: [L2/Mekhane] <- {parent}/ A0->Auto->AddedByCI"

def main():
    if not TARGET_DIR.exists():
        print(f"Error: Directory {TARGET_DIR} not found.")
        sys.exit(1)

    count = 0
    fixed = 0
    skipped = 0

    print(f"Scanning {TARGET_DIR} for missing PROOF headers...")

    for py_file in TARGET_DIR.rglob("*.py"):
        count += 1
        content = py_file.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check if PROOF header exists in first few lines
        has_proof = False
        for i in range(min(5, len(lines))):
            if lines[i].startswith("# PROOF:"):
                has_proof = True
                break

        if has_proof:
            skipped += 1
            continue

        # Prepare header
        parent = py_file.parent.as_posix()
        header = PROOF_TEMPLATE.format(parent=parent)

        # Handle shebang
        new_lines = []
        if lines and lines[0].startswith("#!"):
            new_lines.append(lines[0])
            new_lines.append(header)
            new_lines.extend(lines[1:])
        else:
            new_lines.append(header)
            new_lines.extend(lines)

        # Write back
        # Ensure trailing newline
        new_content = "\n".join(new_lines) + "\n"
        py_file.write_text(new_content, encoding="utf-8")
        print(f"  Fixed: {py_file}")
        fixed += 1

    print("-" * 40)
    print(f"Total files: {count}")
    print(f"Skipped (already has header): {skipped}")
    print(f"Fixed (injected header): {fixed}")

if __name__ == "__main__":
    main()
