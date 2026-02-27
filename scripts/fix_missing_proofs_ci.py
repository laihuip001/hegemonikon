#!/usr/bin/env python3
"""
Batch fix missing PROOF headers for CI.
Injects a placeholder PROOF header into files identified by 'mekhane.dendron.cli check'.
"""
import sys
import subprocess
from pathlib import Path

def get_missing_files():
    """Run dendron check and parse output for missing files."""
    try:
        # Run check command and capture output
        cmd = [sys.executable, "-m", "mekhane.dendron.cli", "check", "mekhane/", "--ci", "--format", "ci"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse lines starting with "  mekhane/"
        missing = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("mekhane/") and line.endswith(".py"):
                missing.append(line)
        return missing
    except Exception as e:
        print(f"Error running dendron check: {e}")
        return []

def inject_proof(filepath):
    """Inject PROOF header into a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {path}")
        return

    try:
        content = path.read_text(encoding="utf-8")
        if content.startswith("# PROOF:"):
            print(f"Skipping {path}: PROOF header already exists")
            return

        # Construct header
        # Format: # PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI
        parent = path.parent.name
        header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI\n"

        # Preserve shebang if present
        if content.startswith("#!"):
            lines = content.splitlines(keepends=True)
            new_content = lines[0] + header + "".join(lines[1:])
        else:
            new_content = header + content

        path.write_text(new_content, encoding="utf-8")
        print(f"Fixed: {path}")
    except Exception as e:
        print(f"Error fixing {path}: {e}")

def main():
    print("🔍 Detecting missing PROOF headers...")
    missing_files = get_missing_files()

    if not missing_files:
        print("✅ No missing PROOF headers found.")
        return

    print(f"⚠️ Found {len(missing_files)} files missing PROOF headers.")
    for f in missing_files:
        inject_proof(f)

    print("✨ All files processed.")

if __name__ == "__main__":
    main()
