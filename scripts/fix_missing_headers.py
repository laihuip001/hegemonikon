#!/usr/bin/env python3
"""
Fix missing PROOF and PURPOSE headers in Python files.
Usage: python scripts/fix_missing_headers.py mekhane/
"""
import sys
import re
from pathlib import Path

def fix_file(filepath: Path):
    content = filepath.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check for PROOF header
    has_proof = any(line.startswith("# PROOF:") for line in lines[:5])

    # Check for PURPOSE header (file level)
    # It usually appears after PROOF or imports, but let's check the first few lines
    has_purpose = any(line.startswith("# PURPOSE:") for line in lines[:20])

    if has_proof and has_purpose:
        return

    print(f"Fixing {filepath} (PROOF={has_proof}, PURPOSE={has_purpose})")

    current_lines = list(lines)

    # Add PROOF if missing
    if not has_proof:
        # Determine L-level based on path
        level = "L2"
        if "hermeneus" in str(filepath): level = "L1"
        elif "kernel" in str(filepath): level = "L0"

        # Generic proof - ensure ASCII arrow
        # Path relative to project root? We can just use the name for now or relative to kwarg
        rel_path = filepath
        try:
             # simplistic relative path attempt
             rel_path = filepath.relative_to(Path.cwd())
        except ValueError:
             pass

        proof_line = f"# PROOF: [{level}/Mekhane] <- {rel_path} O1->Zet->Impl"

        # Insert at top, preserving shebang
        if current_lines and current_lines[0].startswith("#!"):
            current_lines.insert(1, proof_line)
        else:
            current_lines.insert(0, proof_line)

        print(f"  Added PROOF")

    # Add PURPOSE if missing
    if not has_purpose:
        # Try to extract from docstring
        # Look for the first triple-quoted string at the start of the file
        docstring_match = re.search(r'^"""(.*?)"""', content, re.DOTALL | re.MULTILINE)
        purpose_text = "Implementation of module"
        if docstring_match:
            # Get the first non-empty line of the docstring
            ds_content = docstring_match.group(1).strip()
            if ds_content:
                purpose_text = ds_content.split('\n')[0]

        purpose_line = f"# PURPOSE: {purpose_text}"

        # Insert after PROOF (which we just ensured exists or added)
        insert_idx = 0
        for i, line in enumerate(current_lines):
            if line.startswith("# PROOF:"):
                insert_idx = i + 1
                break
            if line.startswith("#!"):
                insert_idx = i + 1

        # If we didn't find PROOF (shouldn't happen if we added it), default to 0 or 1
        current_lines.insert(insert_idx, purpose_line)
        print(f"  Added PURPOSE: {purpose_text}")

    # Write back
    filepath.write_text("\n".join(current_lines) + "\n", encoding="utf-8")

def main():
    root = Path(sys.argv[1])
    for py_file in root.rglob("*.py"):
        # if "tests" in str(py_file): # Keep skipping tests, usually they are exempt or handled differently
        #     continue
        fix_file(py_file)

if __name__ == "__main__":
    main()
