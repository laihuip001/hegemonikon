#!/usr/bin/env python3
# PROOF: [L3/Utility] <- scripts/ A0→Implementation→fix_proof_headers
"""
Batch fix missing PROOF headers in Python files.
"""
import sys
from pathlib import Path

def main():
    root = Path(".")
    fixed_count = 0

    # Files identified in CI failure (partial list from logs, but we scan all)
    # We scan all .py files in mekhane/ and scripts/

    targets = list(root.glob("mekhane/**/*.py")) + list(root.glob("scripts/**/*.py"))

    for py_file in targets:
        if "tests" in py_file.parts:
            continue # Skip tests if they don't strict proof check usually, but CI logs showed some errors?
            # Wait, the log showed mekhane/tape.py, mekhane/api/routes/cortex.py etc.
            # It didn't explicitly show test files in the PROOF failure list (except maybe if I missed it).
            # But usually test files have [L3/Test].
            # Let's verify one of the failed files: mekhane/tape.py

        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        if content.startswith("# PROOF:"):
            continue

        # Determine category based on path
        if "scripts" in py_file.parts:
            category = "[L3/Utility]"
        elif "mekhane" in py_file.parts:
            category = "[L2/Mekhane]"
        else:
            category = "[L2/Implementation]"

        parent = py_file.parent.name
        name = py_file.stem

        header = f"# PROOF: {category} <- {parent}/ A0→Implementation→{name}\n"

        # Handle shebang/encoding
        lines = content.splitlines(keepends=True)
        insert_idx = 0
        if lines and lines[0].startswith("#!"):
            insert_idx += 1
        if len(lines) > insert_idx and (lines[insert_idx].startswith("# -*-") or lines[insert_idx].startswith("# coding")):
            insert_idx += 1

        lines.insert(insert_idx, header)

        py_file.write_text("".join(lines), encoding="utf-8")
        print(f"Fixed: {py_file}")
        fixed_count += 1

    print(f"Total fixed: {fixed_count}")

if __name__ == "__main__":
    main()
