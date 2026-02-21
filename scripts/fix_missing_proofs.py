#!/usr/bin/env python3
# PROOF: [L2/Tool] <- scripts/fix_missing_proofs.py A0->Quality
"""
Fix missing PROOF headers in Python files.

Scans for files missing the '# PROOF:' header and adds a default one.
Preserves shebangs if present.
"""

import sys
from pathlib import Path

# List of files identified in CI failure
MISSING_FILES = [
    "mekhane/tape.py",
    "mekhane/api/routes/cortex.py",
    "mekhane/api/routes/devtools.py",
    "mekhane/mcp/mcp_guard.py",
    "mekhane/mcp/mcp_base.py",
    "mekhane/ccl/ccl_linter.py",
    "mekhane/ccl/operator_loader.py",
    "mekhane/dendron/falsification_checker.py",
    "mekhane/dendron/falsification_matcher.py",
    "mekhane/periskope/cli.py",
    "mekhane/periskope/synthesizer.py",
    "mekhane/periskope/query_expander.py",
    "mekhane/periskope/page_fetcher.py",
    "mekhane/periskope/citation_agent.py",
    "mekhane/periskope/engine.py",
    "mekhane/periskope/__init__.py",
    "mekhane/periskope/models.py",
    "mekhane/periskope/searchers/brave_searcher.py",
    "mekhane/periskope/searchers/internal_searcher.py",
    "mekhane/periskope/searchers/searxng.py",
    "mekhane/periskope/searchers/playwright_searcher.py",
    "mekhane/periskope/searchers/semantic_scholar_searcher.py",
    "mekhane/periskope/searchers/tavily_searcher.py",
    "mekhane/periskope/searchers/__init__.py",
    "mekhane/basanos/l2/g_struct.py",
    "mekhane/basanos/l2/hom.py",
    "mekhane/basanos/l2/cli.py",
    "mekhane/basanos/l2/history.py",
    "mekhane/basanos/l2/resolver.py",
    "mekhane/basanos/l2/models.py",
    "mekhane/basanos/l2/deficit_factories.py",
    "mekhane/basanos/l2/g_semantic.py",
    "mekhane/basanos/l2/__init__.py",
    "mekhane/ochema/ls_launcher.py",
    "mekhane/ochema/fake_extension_server.py",
    "mekhane/ochema/proto/extension_server_pb2_grpc.py",
    "mekhane/ochema/proto/extension_server_pb2.py",
    "mekhane/ochema/proto/__init__.py",
    "mekhane/anamnesis/vertex_embedder.py",
    "mekhane/exagoge/__main__.py"
]

def generate_header(path: Path) -> str:
    """Generate a PROOF header based on file path."""
    # Determine Level/Category
    level = "L2"
    category = "Mekhane"

    parts = path.parts
    if "mekhane" in parts:
        if "periskope" in parts:
            category = "Periskope"
        elif "basanos" in parts:
            category = "Basanos"
        elif "ochema" in parts:
            category = "Ochema"
        elif "ccl" in parts:
            category = "CCL"
        elif "dendron" in parts:
            category = "Dendron"
        elif "mcp" in parts:
            category = "MCP"
        elif "api" in parts:
            category = "API"

    # Format: # PROOF: [L2/Category] <- parent/path/ A0->Auto
    parent_path = str(path.parent) + "/"
    return f"# PROOF: [{level}/{category}] <- {parent_path} A0->AutoFix"

def fix_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping (not found): {filepath}")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if already has header
    if any(line.startswith("# PROOF:") for line in lines[:5]):
        print(f"Skipping (has proof): {filepath}")
        return

    header = generate_header(path)

    # Handle shebang
    if lines and lines[0].startswith("#!"):
        lines.insert(1, header)
    else:
        lines.insert(0, header)

    # Write back
    new_content = "\n".join(lines) + "\n"
    path.write_text(new_content, encoding="utf-8")
    print(f"Fixed: {filepath}")

def main():
    print(f"Fixing {len(MISSING_FILES)} files...")
    for f in MISSING_FILES:
        fix_file(f)
    print("Done.")

if __name__ == "__main__":
    main()
