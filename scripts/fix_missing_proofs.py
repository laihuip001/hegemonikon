#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/ Utility to batch add PROOF headers
"""
Fix Missing Proofs - Batch add PROOF headers to Python files.

Usage:
    python scripts/fix_missing_proofs.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def fix_file(path: Path):
    """Add PROOF header to a file."""
    if not path.exists():
        print(f"Skipping {path} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF header already exists
    if any(line.startswith("# PROOF:") for line in lines):
        print(f"Skipping {path} (already has header)")
        return

    # Construct header
    # Format: # PROOF: [Level/Category] <- path/to/module/
    # Level: L2 (Mekhane) usually

    # Try to determine Category/Level
    try:
        relative_path = path.relative_to(Path.cwd())
    except ValueError:
        # Assuming path is relative to repo root if not absolute
        relative_path = path

    parts = relative_path.parts

    level = "L2"
    category = "Mekhane"

    if len(parts) > 1:
        if parts[0] == "mekhane":
            if parts[1] in ("dendron", "symploke", "ochema", "periskope", "basanos"):
                category = parts[1].capitalize()
            elif parts[1] == "api":
                category = "API"
            elif parts[1] == "mcp":
                category = "MCP"
            elif parts[1] == "ccl":
                category = "CCL"
                level = "L1" # CCL is closer to kernel

    header = f"# PROOF: [{level}/{category}] <- {relative_path.parent}/\n"

    # Insert header
    # If file starts with shebang, insert after it
    if lines and lines[0].startswith("#!"):
        lines.insert(1, header.strip())
    else:
        lines.insert(0, header.strip())

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Fixed {path}")

def main():
    # List of files from the CI failure log
    missing_files = [
        "mekhane/tape.py",
        "mekhane/ccl/operator_loader.py",
        "mekhane/ccl/ccl_linter.py",
        "mekhane/symploke/intent_wal.py",
        "mekhane/mcp/mcp_guard.py",
        "mekhane/mcp/mcp_base.py",
        "mekhane/ochema/ls_launcher.py",
        "mekhane/ochema/fake_extension_server.py",
        "mekhane/dendron/falsification_checker.py",
        "mekhane/dendron/falsification_matcher.py",
        "mekhane/periskope/engine.py",
        "mekhane/periskope/synthesizer.py",
        "mekhane/periskope/models.py",
        "mekhane/periskope/query_expander.py",
        "mekhane/periskope/__init__.py",
        "mekhane/periskope/citation_agent.py",
        "mekhane/periskope/page_fetcher.py",
        "mekhane/periskope/cli.py",
        "mekhane/exagoge/__main__.py",
        "mekhane/anamnesis/vertex_embedder.py",
        "mekhane/ochema/proto/extension_server_pb2_grpc.py",
        "mekhane/ochema/proto/__init__.py",
        "mekhane/ochema/proto/extension_server_pb2.py",
        "mekhane/periskope/searchers/__init__.py",
        "mekhane/periskope/searchers/internal_searcher.py",
        "mekhane/periskope/searchers/tavily_searcher.py",
        "mekhane/periskope/searchers/semantic_scholar_searcher.py",
        "mekhane/periskope/searchers/playwright_searcher.py",
        "mekhane/periskope/searchers/brave_searcher.py",
        "mekhane/periskope/searchers/searxng.py",
        "mekhane/api/routes/cortex.py",
        "mekhane/api/routes/devtools.py",
        "mekhane/basanos/l2/g_semantic.py",
        "mekhane/basanos/l2/resolver.py",
        "mekhane/basanos/l2/models.py",
        "mekhane/basanos/l2/g_struct.py",
        "mekhane/basanos/l2/__init__.py",
        "mekhane/basanos/l2/deficit_factories.py",
        "mekhane/basanos/l2/hom.py",
        "mekhane/basanos/l2/history.py",
        "mekhane/basanos/l2/cli.py",
    ]

    for file_path in missing_files:
        fix_file(Path(file_path))

if __name__ == "__main__":
    main()
