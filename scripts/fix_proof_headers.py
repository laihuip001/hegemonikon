#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/fix_proof_headers.py A0->Auto->AddedByCI
# PURPOSE: Auto-inject missing PROOF headers into files based on Dendron check output

import subprocess
import sys
from pathlib import Path

def main():
    print("Running Dendron check to identify missing headers...")
    try:
        # Run check command and capture output
        result = subprocess.run(
            ["python", "-m", "mekhane.dendron.cli", "check", "mekhane/", "--ci", "--format", "ci"],
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        print("Error: python or module not found.")
        sys.exit(1)

    # Parse stderr/stdout for missing files
    output = result.stdout + result.stderr
    missing_files = []

    # Check output format (based on log: "❌ Dendron: 41 files missing PROOF\n  mekhane/tape.py\n...")
    lines = output.splitlines()
    in_list = False
    for line in lines:
        if "files missing PROOF" in line:
            in_list = True
            continue
        if in_list:
            if line.strip().startswith("mekhane/"):
                missing_files.append(line.strip())
            elif not line.strip() or line.strip().startswith("Purpose:"):
                in_list = False

    if not missing_files:
        print("No missing PROOF headers found or failed to parse output.")
        print("Output was:")
        print(output)
        return

    print(f"Found {len(missing_files)} files missing headers.")

    for rel_path in missing_files:
        path = Path(rel_path)
        if not path.exists():
            print(f"Skipping {path} (not found)")
            continue

        print(f"Fixing {path}...")
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Determine insertion point (after shebang if present)
        insert_idx = 0
        if lines and lines[0].startswith("#!"):
            insert_idx = 1

        # Prepare header
        header = f"# PROOF: [L2/Mekhane] <- {rel_path} A0->Auto->AddedByCI"

        # Insert
        lines.insert(insert_idx, header)

        # Write back
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Done.")

if __name__ == "__main__":
    main()
