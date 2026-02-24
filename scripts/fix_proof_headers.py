#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/fix_proof_headers.py A0->Auto->Fixer
"""
Fix missing PROOF headers in Python files.
"""
import sys
from pathlib import Path

def fix_file(path: Path):
    if not path.exists() or path.suffix != ".py":
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    if not lines:
        return

    # Check if PROOF header exists
    has_proof = any(line.startswith("# PROOF:") for line in lines[:5])
    if has_proof:
        return

    # Determine insertion point (after shebang if present)
    insert_idx = 0
    if lines[0].startswith("#!"):
        insert_idx = 1

    # Construct header
    # Heuristic: Use parent directory as source
    parent = path.parent.name
    header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI"

    lines.insert(insert_idx, header)

    # Write back
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Fixed: {path}")

def main():
    root = Path("mekhane")
    for py_file in root.rglob("*.py"):
        fix_file(py_file)

if __name__ == "__main__":
    main()
