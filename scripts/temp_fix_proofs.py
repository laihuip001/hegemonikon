#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/scripts/ A0->Auto->FixProofs
# PURPOSE: Auto-inject missing PROOF headers into files reported by Dendron CLI
"""
Parses Dendron CLI JSON output and injects missing PROOF headers.
"""

import json
import subprocess
import sys
from pathlib import Path

def main():
    # Run dendron check
    print("Running Dendron check...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mekhane.dendron.cli", "check", "mekhane/", "--format", "json"],
            capture_output=True,
            text=True
        )
    except Exception as e:
        print(f"Failed to run dendron check: {e}")
        return

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        # If no JSON, maybe no errors? or check stderr
        if "Missing PROOF" in result.stdout or "Missing PROOF" in result.stderr:
             # Fallback: parse text output if JSON fails?
             # But we asked for JSON. If it fails, maybe there are no errors or partial output.
             print("Could not parse JSON output. Raw output:")
             print(result.stdout)
             print(result.stderr)
             return
        print("No JSON output, assuming pass.")
        return

    missing_files = data.get("missing_files", [])
    if not missing_files:
        print("No missing PROOF headers found.")
        return

    print(f"Found {len(missing_files)} files missing PROOF headers.")

    for file_path_str in missing_files:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue

        print(f"Fixing {file_path}...")

        # Determine parent dir for context
        parent_dir = file_path.parent.name
        header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent_dir}/ A0->Auto->AddedByCI\n"

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines(keepends=True)

            # Handle shebang
            if lines and lines[0].startswith("#!"):
                lines.insert(1, header)
            else:
                lines.insert(0, header)

            file_path.write_text("".join(lines), encoding="utf-8")
        except Exception as e:
            print(f"Failed to fix {file_path}: {e}")

    print("Done.")

if __name__ == "__main__":
    main()
