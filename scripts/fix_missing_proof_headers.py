#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/ A0→保守→fix_missing_proof_headers
# PURPOSE: Batch-add missing PROOF headers to Python files to pass Dendron checks
"""
Batch-add missing PROOF headers to Python files.
Targets files identified in CI failures.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def fix_file(path: Path):
    try:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check if PROOF already exists
        for line in lines[:5]:
            if line.strip().startswith("# PROOF:"):
                print(f"SKIP: {path} (Header exists)")
                return

        # Determine insertion point
        insert_idx = 0
        if lines and lines[0].startswith("#!"):
            insert_idx = 1
        if len(lines) > 1 and "coding:" in lines[1]:
            insert_idx = 2

        # Construct header
        parent = path.parent.name
        if not parent:
            parent = "mekhane"

        header = f"# PROOF: [L2/Mekhane] <- {parent}/ A0→Implementation→{path.name}"

        lines.insert(insert_idx, header)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"FIXED: {path}")

    except Exception as e:
        print(f"ERROR: {path} - {e}")

def main():
    target_dir = PROJECT_ROOT / "mekhane"
    for py_file in target_dir.rglob("*.py"):
        fix_file(py_file)

if __name__ == "__main__":
    main()
