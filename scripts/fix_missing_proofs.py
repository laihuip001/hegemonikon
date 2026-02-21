#!/usr/bin/env python3
# PURPOSE: Fix missing PROOF headers in Python files
# PROOF: [L2/Mekhane] <- scripts/fix_missing_proofs.py Auto-generated proof header
"""
Fix missing PROOF headers in Python files.
"""

import sys
from pathlib import Path

# PURPOSE: Main execution
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/fix_missing_proofs.py <file1> <file2> ...")
        sys.exit(1)

    for file_path in sys.argv[1:]:
        path = Path(file_path)
        if not path.exists():
            print(f"File not found: {file_path}")
            continue

        try:
            content = path.read_text(encoding="utf-8")

            # Check if shebang is present
            has_shebang = content.startswith("#!")
            lines = content.splitlines()

            # Check if PROOF header is already present
            if any(line.startswith("# PROOF:") for line in lines[:5]):
                print(f"Skipping {file_path}: PROOF header already present")
                continue

            # Construct the PROOF header
            parent_dir = path.parent.name
            proof_header = f"# PROOF: [L2/Mekhane] <- {path.parent}/ Auto-generated proof header"

            new_lines = []
            if has_shebang:
                new_lines.append(lines[0])
                new_lines.append(proof_header)
                new_lines.extend(lines[1:])
            else:
                new_lines.append(proof_header)
                new_lines.extend(lines)

            # Write back to file
            path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            print(f"Fixed {file_path}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    main()
