#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/scripts/ A0->Auto->AddedByCI
# PURPOSE: Inject missing PROOF headers into Python files for CI compliance
import sys
import re
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python inject_missing_proof_headers.py <directory>")
        sys.exit(1)

    target_dir = Path(sys.argv[1])
    if not target_dir.exists():
        print(f"Error: {target_dir} does not exist")
        sys.exit(1)

    # Regex for PROOF header
    proof_pattern = re.compile(r"^# PROOF: \[.+?\] <- .+? .*$")

    count = 0
    for py_file in target_dir.rglob("*.py"):
        if py_file.name == "__init__.py" and py_file.stat().st_size == 0:
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"Skipping binary/unreadable file: {py_file}")
            continue

        lines = content.splitlines()
        has_proof = False

        # Check first few lines for PROOF
        for line in lines[:5]:
            if proof_pattern.match(line):
                has_proof = True
                break

        if has_proof:
            continue

        # Prepare header
        # Pattern: # PROOF: [L2/Mekhane] <- mekhane/{parent_dir}/ A0->Auto->AddedByCI
        # Calculate relative parent path for better context if possible
        try:
            rel_path = py_file.relative_to(Path.cwd())
            parent = rel_path.parent
        except ValueError:
            parent = py_file.parent

        header = f"# PROOF: [L2/Mekhane] <- {parent}/ A0->Auto->AddedByCI"

        new_lines = []
        inserted = False

        # Insert after shebang if exists
        if lines and lines[0].startswith("#!"):
            new_lines.append(lines[0])
            new_lines.append(header)
            new_lines.extend(lines[1:])
            inserted = True
        else:
            new_lines.append(header)
            new_lines.extend(lines)
            inserted = True

        if inserted:
            print(f"Injecting header into: {py_file}")
            py_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            count += 1

    print(f"Injected headers into {count} files.")

if __name__ == "__main__":
    main()
