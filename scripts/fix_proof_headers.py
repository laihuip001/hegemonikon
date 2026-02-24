# PROOF: [L2/Mekhane] <- scripts/fix_proof_headers.py A0->Auto->AddedByCI
"""
Fix missing PROOF headers in Python files.
"""

import sys
from pathlib import Path

def main():
    root = Path(".")

    # Read missing files from stdin if piped, otherwise scan mekhane
    missing_files = []

    # Run dendron check and capture output
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mekhane.dendron.cli", "check", "mekhane/", "--ci", "--format", "ci"],
            capture_output=True,
            text=True
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("mekhane/") and line.endswith(".py"):
                 missing_files.append(line)
    except Exception as e:
        print(f"Error running dendron check: {e}")
        return

    print(f"Found {len(missing_files)} files missing PROOF headers.")

    count = 0
    for file_path_str in missing_files:
        path = root / file_path_str
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check if already has PROOF
        if any(line.startswith("# PROOF:") for line in lines):
            continue

        # Determine insertion point (after shebang or at top)
        new_lines = []
        header = "# PROOF: [L2/Mekhane] <- " + file_path_str + " A0->Auto->AddedByCI"

        if lines and lines[0].startswith("#!"):
            new_lines.append(lines[0])
            new_lines.append(header)
            new_lines.extend(lines[1:])
        else:
            new_lines.append(header)
            new_lines.extend(lines)

        # Write back
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"Fixed: {file_path_str}")
        count += 1

    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
