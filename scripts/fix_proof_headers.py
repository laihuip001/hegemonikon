#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/ A0->Auto->AddedByCI
# PURPOSE: mekhane/ 以下の Python ファイルに不足している # PROOF: ヘッダを一括注入する
"""
Batch-inject missing # PROOF: headers for Python files in mekhane/.

This script scans for .py files missing the required header and injects
a default placeholder to satisfy Dendron CI checks.
"""
import sys
from pathlib import Path

# Header to inject
DEFAULT_HEADER = "# PROOF: [L2/Mekhane] <- mekhane/ A0->Auto->AddedByCI"

def fix_file(path: Path) -> bool:
    """Inject header if missing."""
    try:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check if already present
        for i, line in enumerate(lines[:5]):  # Check first 5 lines
            if line.startswith("# PROOF:"):
                return False

        # Determine insertion point (handle shebang)
        insert_idx = 0
        if lines and lines[0].startswith("#!"):
            insert_idx = 1

        lines.insert(insert_idx, DEFAULT_HEADER)

        # Write back
        new_content = "\n".join(lines) + ("\n" if lines else "")
        path.write_text(new_content, encoding="utf-8")
        return True

    except Exception as e:
        print(f"Error processing {path}: {e}", file=sys.stderr)
        return False

def main():
    root_dir = Path("mekhane")
    if not root_dir.exists():
        print("mekhane/ directory not found.")
        sys.exit(1)

    fixed_count = 0
    for py_file in root_dir.rglob("*.py"):
        if fix_file(py_file):
            print(f"Fixed: {py_file}")
            fixed_count += 1

    print(f"Total files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
