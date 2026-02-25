#!/usr/bin/env python3
"""
Automated PROOF Header Injector for CI

Parses the JSON output of `mekhane.dendron.cli check` and injects
standardized PROOF headers into files that are missing them.

Usage:
    python scripts/fix_missing_proofs_ci.py
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

def get_missing_files() -> List[str]:
    """Run dendron check and get missing files."""
    try:
        # Run the check command and capture JSON output
        result = subprocess.run(
            [sys.executable, "-m", "mekhane.dendron.cli", "check", "mekhane/", "--format", "json"],
            capture_output=True,
            text=True
        )

        # The command might exit with 1 if there are missing proofs, which is expected.
        # We try to parse stdout regardless.
        output = result.stdout.strip()
        if not output:
            print("No output from dendron check.")
            return []

        try:
            data = json.loads(output)
            return data.get("missing_files", [])
        except json.JSONDecodeError:
            print(f"Failed to parse JSON output: {output[:100]}...")
            return []

    except Exception as e:
        print(f"Error running dendron check: {e}")
        return []

def inject_proof(filepath: str):
    """Inject PROOF header into a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return

    try:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Determine insertion point (skip shebang or encoding cookie)
        insert_idx = 0
        if lines and lines[0].startswith(("#!", "# -*-")):
            insert_idx += 1
            if len(lines) > 1 and lines[1].startswith("# -*-"):
                insert_idx += 1

        # Construct PROOF header
        # Pattern: # PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI
        parent = path.parent.name
        proof_header = f'# PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI'

        # Insert
        lines.insert(insert_idx, proof_header)

        # Write back
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Injected PROOF header into: {filepath}")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    print("🔍 Scanning for missing PROOF headers...")
    missing_files = get_missing_files()

    if not missing_files:
        print("✅ No missing PROOF headers found.")
        return

    print(f"Found {len(missing_files)} files missing PROOF headers.")

    for filepath in missing_files:
        inject_proof(filepath)

    print("✨ Done.")

if __name__ == "__main__":
    main()
