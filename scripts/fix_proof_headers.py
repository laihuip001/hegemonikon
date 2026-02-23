#!/usr/bin/env python3
"""
Fix missing PROOF headers in Python files.
Usage: python scripts/fix_proof_headers.py
"""
import sys
from pathlib import Path

# Files listed in the CI failure log
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
    "mekhane/symploke/intent_wal.py",
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
    "mekhane/basanos/l2/__init__.py",
    "mekhane/basanos/l2/models.py",
    "mekhane/basanos/l2/deficit_factories.py",
    "mekhane/basanos/l2/g_semantic.py",
    "mekhane/ochema/ls_launcher.py",
    "mekhane/ochema/fake_extension_server.py",
    "mekhane/ochema/proto/extension_server_pb2_grpc.py",
    "mekhane/ochema/proto/extension_server_pb2.py",
    "mekhane/ochema/proto/__init__.py",
    "mekhane/anamnesis/vertex_embedder.py",
    "mekhane/exagoge/__main__.py",
]

def fix_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping (not found): {filepath}")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if header already exists (simple check)
    if any(line.startswith("# PROOF:") for line in lines[:5]):
        print(f"Skipping (header exists): {filepath}")
        return

    # Determine category based on path
    category = "L2/Mekhane"
    if "api/routes" in filepath:
        category = "L2/API"
    elif "mcp" in filepath:
        category = "L2/MCP"
    elif "ccl" in filepath:
        category = "L2/CCL"
    elif "dendron" in filepath:
        category = "L2/Dendron"
    elif "symploke" in filepath:
        category = "L2/Symploke"
    elif "periskope" in filepath:
        category = "L2/Periskope"
    elif "basanos" in filepath:
        category = "L2/Basanos"
    elif "ochema" in filepath:
        category = "L2/Ochema"

    # ASCII arrow "->" is required, not unicode
    header = f"# PROOF: [{category}] <- {filepath} A0->Need->Implementation"

    # Insert after shebang if present
    if lines and lines[0].startswith("#!"):
        lines.insert(1, header)
    else:
        lines.insert(0, header)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Fixed: {filepath}")

def main():
    print(f"Fixing {len(MISSING_FILES)} files...")
    for f in MISSING_FILES:
        fix_file(f)
    print("Done.")

if __name__ == "__main__":
    main()
