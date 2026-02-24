#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/fix_proof_headers.py A0->Auto->Fixer
# PURPOSE: Missing PROOF headers を自動修復する
"""
Fix missing # PROOF: headers in Python files.

Scans mekhane/ and hermeneus/ for .py files missing the PROOF header.
Injects a default header:
# PROOF: [L2/Mekhane] <- {filepath} A0->Auto->AddedByCI

Preserves shebang lines.
"""
import os
from pathlib import Path

# Directories to scan
TARGET_DIRS = ["mekhane", "hermeneus"]

def fix_file(filepath: Path):
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check if already has PROOF
        if any(line.startswith("# PROOF:") for line in lines[:5]):
            return

        print(f"Fixing {filepath}")

        header = f"# PROOF: [L2/Mekhane] <- {filepath} A0->Auto->AddedByCI"

        new_lines = []
        if lines and lines[0].startswith("#!"):
            new_lines.append(lines[0])
            new_lines.append(header)
            new_lines.extend(lines[1:])
        else:
            new_lines.append(header)
            new_lines.extend(lines)

        # Ensure newline at end
        new_content = "\n".join(new_lines) + "\n"
        filepath.write_text(new_content, encoding="utf-8")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    root = Path(".")
    count = 0
    for target in TARGET_DIRS:
        target_path = root / target
        if not target_path.exists():
            continue

        for filepath in target_path.rglob("*.py"):
            fix_file(filepath)
            count += 1

    print(f"Scanned {count} files.")

if __name__ == "__main__":
    main()
