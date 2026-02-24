#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/fix_proof_headers.py A0->Quality->Automation
# PURPOSE: Automatically inject missing PROOF headers into Python files.

import sys
import re
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: fix_proof_headers.py <directory>")
        sys.exit(1)

    target_dir = Path(sys.argv[1])
    if not target_dir.exists():
        print(f"Error: {target_dir} does not exist")
        sys.exit(1)

    count = 0
    for py_file in target_dir.glob("**/*.py"):
        if py_file.is_file():
            content = py_file.read_text(encoding="utf-8")
            lines = content.splitlines()

            has_proof = False
            for line in lines[:5]:  # Check first 5 lines
                if line.startswith("# PROOF:"):
                    has_proof = True
                    break

            if not has_proof:
                print(f"Fixing {py_file}...")
                relative_path = py_file.relative_to(Path.cwd()) if py_file.is_absolute() else py_file
                proof_header = f"# PROOF: [L2/Mekhane] <- {relative_path} A0->Common->Module"

                # Preserve shebang if present
                if lines and lines[0].startswith("#!"):
                    lines.insert(1, proof_header)
                else:
                    lines.insert(0, proof_header)

                py_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                count += 1

    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
