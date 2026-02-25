#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/ A0→保守→fix_missing_proof_headers
# PURPOSE: CIで検出された欠損PROOFヘッダを一括追加する
"""
Fix Missing PROOF Headers

Scans the `mekhane/` directory for Python files missing the `# PROOF:` header
and inserts a default one. This is to resolve CI failures in the PROOF Check.

Usage:
    python scripts/fix_missing_proof_headers.py
"""

from pathlib import Path
import sys

TARGET_DIR = Path("mekhane")

def fix_file(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)

        # Check if PROOF exists in first few lines
        for i, line in enumerate(lines[:5]):
            if line.strip().startswith("# PROOF:"):
                return False  # Already has proof

        # Determine insertion point
        insert_idx = 0
        if lines and lines[0].startswith("#!"):
            insert_idx = 1
            # Check encoding cookie on line 2
            if len(lines) > 1 and "coding:" in lines[1]:
                insert_idx = 2

        # Construct header
        # Format: # PROOF: [Category] <- {parent}/ A0→AutoFix→{name}
        category = "[L2/Mekhane]"
        if "tests" in path.parts:
            category = "[L3/Test]"
        elif "scripts" in path.parts:
            category = "[L3/Utility]"

        parent = path.parent.name
        name = path.stem
        header = f"# PROOF: {category} <- {path.parent}/ A0→AutoFix→{name}\n"

        lines.insert(insert_idx, header)

        path.write_text("".join(lines), encoding="utf-8")
        print(f"Fixed: {path}")
        return True

    except Exception as e:
        print(f"Error processing {path}: {e}")
        return False

def main():
    if not TARGET_DIR.exists():
        print(f"Directory {TARGET_DIR} not found.")
        sys.exit(1)

    count = 0
    for py_file in TARGET_DIR.rglob("*.py"):
        if fix_file(py_file):
            count += 1

    print(f"Total files fixed: {count}")

if __name__ == "__main__":
    main()
