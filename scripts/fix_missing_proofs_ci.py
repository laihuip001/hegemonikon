#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/ A0->Auto->FixMissingProofsCI
# PURPOSE: Batch inject missing PROOF headers for CI compliance
"""
Batch inject missing PROOF headers for CI compliance.
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Fix missing PROOF headers")
    parser.add_argument("target_dir", type=str, help="Target directory")
    parser.add_argument("--write", action="store_true", help="Write changes")
    args = parser.parse_args()

    target_dir = Path(args.target_dir)
    if not target_dir.exists():
        print(f"Error: {target_dir} not found")
        sys.exit(1)

    count = 0
    for py_file in target_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
            continue

        if content.startswith("# PROOF:"):
            continue

        # Generate proof
        parent = py_file.parent.name
        proof_line = f"# PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI\n"

        if args.write:
            py_file.write_text(proof_line + content, encoding="utf-8")
            print(f"Fixed: {py_file}")
        else:
            print(f"Would fix: {py_file}")

        count += 1

    print(f"Total fixed: {count}")

if __name__ == "__main__":
    main()
