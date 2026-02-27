#!/usr/bin/env python3
"""
Batch add PROOF headers to Python files missing them.
Usage: python scripts/fix_missing_proof_headers_v2.py
"""
import os
import re
from pathlib import Path

# Regex for existing PROOF header (strict)
PROOF_REGEX = re.compile(r"^#\s*PROOF:\s*\[([^\]]+)\](?:\s*<-\s*([^\s#]+))?")
SHEBANG_REGEX = re.compile(r"^#!.*python.*")

# Default PROOF values based on directory
DEFAULT_PROOFS = {
    "mekhane/dendron": "[L2/Quality] <- mekhane/dendron/ Dendron Quality Guard",
    "mekhane/symploke": "[L2/Mekhane] <- mekhane/symploke/ Specialist Review",
    "mekhane/pks": "[L2/PKS] <- mekhane/pks/ PKS Engine",
    "mekhane/basanos": "[L2/Basanos] <- mekhane/basanos/ Basanos Engine",
    "mekhane/ochema": "[L2/Ochema] <- mekhane/ochema/ Ochema Routing",
    "mekhane/periskope": "[L2/Periskope] <- mekhane/periskope/ Periskope Search",
    "mekhane/ccl": "[L2/CCL] <- mekhane/ccl/ CCL Macros",
    "mekhane/anamnesis": "[L2/Anamnesis] <- mekhane/anamnesis/ Anamnesis Memory",
    "mekhane/mcp": "[L2/MCP] <- mekhane/mcp/ MCP Server",
    "mekhane/exagoge": "[L2/Exagoge] <- mekhane/exagoge/ Exagoge Export",
    "mekhane/api": "[L2/API] <- mekhane/api/ API Server",
    "mekhane": "[L2/Mekhane] <- mekhane/ Implementation Layer",
}

def get_proof_for_file(filepath):
    """Determine the PROOF header based on the file path."""
    path_str = str(filepath)
    # Match specific directories first (longest match)
    best_match = None
    max_len = 0

    for prefix, proof in DEFAULT_PROOFS.items():
        if path_str.startswith(prefix) and len(prefix) > max_len:
            best_match = proof
            max_len = len(prefix)

    if best_match:
        # Append filename description
        name = filepath.name.replace(".py", "").replace("_", " ").title()
        return f"# PROOF: {best_match} {name}"

    return f"# PROOF: [L2/Unknown] <- {filepath.parent}/ Unknown Module"

def process_file(filepath):
    """Check and add PROOF header if missing."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return  # Skip binary or unreadable files

    lines = content.splitlines()
    if not lines and os.stat(filepath).st_size == 0:
        return # Skip empty files

    has_proof = False
    for line in lines[:5]: # Check first 5 lines
        if PROOF_REGEX.match(line):
            has_proof = True
            break

    if has_proof:
        return

    # Determine insertion point (after shebang if present)
    insert_idx = 0
    if lines and SHEBANG_REGEX.match(lines[0]):
        insert_idx = 1

    proof_header = get_proof_for_file(filepath)
    print(f"Adding header to {filepath}: {proof_header}")

    new_lines = lines[:insert_idx] + [proof_header] + lines[insert_idx:]
    # Ensure newline at EOF
    new_content = "\n".join(new_lines) + "\n"

    filepath.write_text(new_content, encoding="utf-8")

def main():
    root_dirs = ["mekhane"]

    for root in root_dirs:
        for path in Path(root).rglob("*.py"):
            if "node_modules" in str(path) or "__pycache__" in str(path):
                continue
            process_file(path)

if __name__ == "__main__":
    main()
