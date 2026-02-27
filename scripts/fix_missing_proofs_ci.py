#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/ A0->Auto->AddedByCI
"""
Fix Missing Proofs CI - Batch inject missing PROOF headers

CI で PROOF ヘッダ不足が検出されたファイルに対して、
標準的なプレースホルダー PROOF ヘッダを自動注入する。

Usage:
    python scripts/fix_missing_proofs_ci.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def fix_missing_proofs():
    """Run dendron check and fix missing proofs."""
    print("🔍 Scanning for missing PROOF headers...")

    # Check all files under mekhane/ and hermeneus/
    targets = [
        PROJECT_ROOT / "mekhane",
        PROJECT_ROOT / "hermeneus",
    ]

    missing_files = []

    for target in targets:
        for py_file in target.glob("**/*.py"):
            if py_file.is_file():
                content = py_file.read_text(encoding="utf-8")
                if not content.startswith("# PROOF:"):
                    missing_files.append(py_file)

    if not missing_files:
        print("✅ No missing PROOF headers found.")
        return

    print(f"🔧 Fixing {len(missing_files)} files...")

    for py_file in missing_files:
        print(f"  - {py_file.relative_to(PROJECT_ROOT)}")

        # Determine L-level based on path
        rel_path = py_file.relative_to(PROJECT_ROOT)
        level = "L2/Mekhane"
        if str(rel_path).startswith("hermeneus"):
            level = "L1/Hermeneus"
        elif str(rel_path).startswith("kernel"):
            level = "L0/Kernel"

        parent = py_file.parent.name
        header = f"# PROOF: [{level}] <- {rel_path.parent}/ A0->Auto->AddedByCI\n"

        content = py_file.read_text(encoding="utf-8")

        # Handle shebang
        if content.startswith("#!"):
            lines = content.splitlines(keepends=True)
            if len(lines) > 0:
                lines.insert(1, header)
                new_content = "".join(lines)
            else:
                new_content = header + content
        else:
            new_content = header + content

        py_file.write_text(new_content, encoding="utf-8")

    print(f"✨ Fixed {len(missing_files)} files.")

if __name__ == "__main__":
    fix_missing_proofs()
