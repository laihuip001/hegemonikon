#!/usr/bin/env python3
"""Batch add missing PROOF headers to mekhane/."""
import sys
from pathlib import Path

def main():
    root = Path("mekhane")
    if not root.exists():
        print("mekhane/ not found")
        sys.exit(1)

    count = 0
    for fpath in root.rglob("*.py"):
        if fpath.name == "__init__.py" and fpath.stat().st_size == 0:
            continue

        try:
            content = fpath.read_text(encoding="utf-8")
        except Exception:
            continue

        # Check if PROOF exists in first few lines
        lines = content.splitlines(keepends=True)
        has_proof = False
        for i in range(min(5, len(lines))):
            if lines[i].startswith("# PROOF:"):
                has_proof = True
                break

        if has_proof:
            continue

        # Determine Category
        path_str = str(fpath)
        category = "[L2/Mekhane]"
        if "dendron" in path_str: category = "[L2/Quality]"
        elif "symploke" in path_str: category = "[L2/Infra]"
        elif "periskope" in path_str: category = "[L2/Search]"
        elif "basanos" in path_str: category = "[L2/Test]"
        elif "ochema" in path_str: category = "[L2/Orchestration]"
        elif "ccl" in path_str: category = "[L2/Language]"
        elif "api" in path_str: category = "[L2/API]"
        elif "mcp" in path_str: category = "[L2/MCP]"

        rel_parent = str(fpath.parent) + "/"
        module_name = fpath.name
        header = f"# PROOF: {category} <- {rel_parent} A0→Implementation→{module_name}\n"

        # Insert
        insert_idx = 0
        if lines and lines[0].startswith("#!"):
            insert_idx = 1
        elif lines and lines[0].startswith("# -*-"):
            insert_idx = 1

        lines.insert(insert_idx, header)
        fpath.write_text("".join(lines), encoding="utf-8")
        print(f"Added PROOF to {fpath}")
        count += 1

    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
