#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/fix_missing_proof_headers_v2.py A0→BatchFix→Quality
"""
Batch-add missing PROOF headers to Python files.
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

    count = 0
    for py_file in mekhane_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            if "# PROOF:" not in content.split("\n", 1)[0]:
                header = get_template(py_file.relative_to(root))
                # Handle shebang
                lines = content.splitlines()
                if lines and lines[0].startswith("#!"):
                    lines.insert(1, header)
                else:
                    lines.insert(0, header)

                py_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                print(f"Fixed: {py_file}")
                count += 1
        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    print(f"Added headers to {count} files.")

if __name__ == "__main__":
    main()
