#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/fix_missing_proof_headers_v2.py A0→BatchFix→Quality
"""
Batch-add missing PROOF headers to Python files and clean up duplicates.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Default proof templates by directory
TEMPLATES = {
    "mekhane/dendron": "# PROOF: [L2/Quality] <- {path} S2→Quality→Dendron",
    "mekhane/basanos": "# PROOF: [L2/Test] <- {path} A2→Test→Basanos",
    "mekhane/symploke": "# PROOF: [L2/Infra] <- {path} H3→Infra→Symploke",
    "mekhane/ochema": "# PROOF: [L2/Mekhane] <- {path} S2→Mekhane→Ochema",
    "mekhane/api": "# PROOF: [L2/Mekhane] <- {path} S2→Mekhane→API",
    "mekhane/mcp": "# PROOF: [L2/Mekhane] <- {path} S2→Mekhane→MCP",
    "mekhane/periskope": "# PROOF: [L2/Mekhane] <- {path} S2→Mekhane→Periskope",
    "mekhane/ccl": "# PROOF: [L2/Mekhane] <- {path} S2→Mekhane→CCL",
    "default": "# PROOF: [L2/Mekhane] <- {path} S2→Mekhane→Implementation",
}

def get_template(path: Path) -> str:
    path_str = str(path)
    for key, template in TEMPLATES.items():
        if key in path_str and key != "default":
            return template.format(path=path_str)
    return TEMPLATES["default"].format(path=path_str)

def main():
    root = Path.cwd()
    mekhane_dir = root / "mekhane"

    added_count = 0
    deduped_count = 0

    for py_file in mekhane_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            lines = content.splitlines()

            # 1. Clean up duplicates (keep only the first PROOF header)
            proof_lines_indices = [i for i, line in enumerate(lines) if line.startswith("# PROOF:")]

            if len(proof_lines_indices) > 1:
                # Keep the first one, remove others
                # Iterate backwards to avoid index shifting
                for i in reversed(proof_lines_indices[1:]):
                    lines.pop(i)
                deduped_count += 1

                # Write back immediately to be clean for next check
                content = "\n".join(lines) + "\n"
                py_file.write_text(content, encoding="utf-8")
                # Reload lines
                lines = content.splitlines()

            # 2. Check if missing (scan first 5 lines to be safe against shebangs/comments)
            has_proof = False
            for line in lines[:5]:
                if line.startswith("# PROOF:"):
                    has_proof = True
                    break

            if not has_proof:
                header = get_template(py_file.relative_to(root))
                if lines and lines[0].startswith("#!"):
                    lines.insert(1, header)
                else:
                    lines.insert(0, header)

                py_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                print(f"Fixed (Added): {py_file}")
                added_count += 1
            elif deduped_count > 0 and py_file in [Path(f) for f in sys.argv]: # Only print if explicitly modified
                 pass

        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    print(f"Summary: Added headers to {added_count} files. Deduped {deduped_count} files.")

if __name__ == "__main__":
    main()
