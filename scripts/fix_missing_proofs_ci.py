#!/usr/bin/env python3
"""
Fix missing PROOF headers in CI.
Iterates over all .py files in mekhane/ and adds a PROOF header if missing.
"""

import os
from pathlib import Path

def main() -> None:
    root = Path("mekhane")
    count = 0

    for path in root.rglob("*.py"):
        if not path.is_file():
            continue

        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        has_proof = False
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith("# PROOF:"):
                has_proof = True
                break

        if not has_proof:
            print(f"Fixing: {path}")

            # Determine parent directory for context
            parent = path.parent.name

            # Construct standard header
            # PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI
            header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI"

            # Insert after shebang if present, otherwise at top
            new_lines = []
            if lines and lines[0].startswith("#!"):
                new_lines.append(lines[0])
                new_lines.append(header)
                new_lines.extend(lines[1:])
            else:
                new_lines.append(header)
                new_lines.extend(lines)

            path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            count += 1

    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
