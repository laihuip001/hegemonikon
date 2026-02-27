#!/usr/bin/env python3
"""
Batch inject standardized PROOF headers into files identified by CI as missing them.
"""
import os
from pathlib import Path

def main():
    root_dir = Path("mekhane")
    if not root_dir.exists():
        print("Mekhane directory not found.")
        return

    count = 0
    for path in root_dir.rglob("*.py"):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue

        try:
            content = path.read_text(encoding="utf-8")
            if not content.startswith("# PROOF:"):
                # Construct parent path for the proof trace
                parent = path.parent.name
                proof_header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI\n"

                # Check for shebang
                if content.startswith("#!"):
                    lines = content.splitlines()
                    lines.insert(1, proof_header.strip())
                    new_content = "\n".join(lines) + "\n"
                else:
                    new_content = proof_header + content

                path.write_text(new_content, encoding="utf-8")
                print(f"Added PROOF to {path}")
                count += 1
        except Exception as e:
            print(f"Error processing {path}: {e}")

    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
