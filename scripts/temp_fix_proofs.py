#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/ A0->Auto->AddedByCI
# PURPOSE: Automatically inject missing PROOF headers into files identified by Dendron CLI
"""
Temp Fix Proofs - Missing PROOF header injector

Usage:
    python scripts/temp_fix_proofs.py
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List

def get_missing_files() -> List[str]:
    """Get list of files missing PROOF headers using Dendron CLI."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mekhane.dendron.cli", "check", "mekhane/", "--format", "json"],
            capture_output=True,
            text=True,
            check=False
        )
        data = json.loads(result.stdout)
        return data.get("missing_files", [])
    except Exception as e:
        print(f"Error getting missing files: {e}", file=sys.stderr)
        return []

def inject_header(filepath: str) -> None:
    """Inject PROOF header into a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}", file=sys.stderr)
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Determine header content
    # parent_dir should reflect the logical parent path
    # e.g. mekhane/tape.py -> mekhane/
    parent = path.parent
    # Ensure parent ends with slash for consistency with convention
    parent_str = str(parent)
    if not parent_str.endswith("/"):
        parent_str += "/"

    header = f"# PROOF: [L2/Mekhane] <- {parent_str} A0->Auto->AddedByCI"

    # Check for shebang
    if lines and lines[0].startswith("#!"):
        # Insert after shebang
        new_lines = [lines[0], header] + lines[1:]
    else:
        # Insert at top
        new_lines = [header] + lines

    # Write back
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"Fixed: {filepath}")

def main() -> None:
    """Main execution."""
    missing = get_missing_files()
    if not missing:
        print("No missing files found.")
        return

    print(f"Found {len(missing)} files missing PROOF headers.")
    for f in missing:
        inject_header(f)
    print("Done.")

if __name__ == "__main__":
    main()
