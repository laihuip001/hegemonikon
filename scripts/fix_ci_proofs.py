#!/usr/bin/env python3
"""Batch add missing PROOF headers to files listed in CI failure."""

import os
from pathlib import Path

# List of files from CI log
FILES = [
    "mekhane/tape.py",
    "mekhane/anamnesis/vertex_embedder.py",
    "mekhane/mcp/mcp_guard.py",
    "mekhane/mcp/mcp_base.py",
    "mekhane/dendron/falsification_checker.py",
    "mekhane/dendron/falsification_matcher.py",
    "mekhane/periskope/citation_agent.py",
    "mekhane/periskope/models.py",
    "mekhane/periskope/__init__.py",
    "mekhane/periskope/cli.py",
    "mekhane/periskope/engine.py",
    "mekhane/periskope/query_expander.py",
    "mekhane/periskope/synthesizer.py",
    "mekhane/periskope/page_fetcher.py",
    "mekhane/periskope/searchers/searxng.py",
    "mekhane/periskope/searchers/brave_searcher.py",
    "mekhane/periskope/searchers/tavily_searcher.py",
    "mekhane/periskope/searchers/__init__.py",
    "mekhane/periskope/searchers/internal_searcher.py",
    "mekhane/periskope/searchers/playwright_searcher.py",
    "mekhane/periskope/searchers/semantic_scholar_searcher.py",
    "mekhane/ccl/operator_loader.py",
    "mekhane/ccl/ccl_linter.py",
    "mekhane/exagoge/__main__.py",
    "mekhane/api/routes/cortex.py",
    "mekhane/api/routes/devtools.py",
    "mekhane/basanos/l2/hom.py",
    "mekhane/basanos/l2/deficit_factories.py",
    "mekhane/basanos/l2/models.py",
    "mekhane/basanos/l2/history.py",
    "mekhane/basanos/l2/resolver.py",
    "mekhane/basanos/l2/__init__.py",
    "mekhane/basanos/l2/cli.py",
    "mekhane/basanos/l2/g_semantic.py",
    "mekhane/basanos/l2/g_struct.py",
    "mekhane/ochema/ls_launcher.py",
    "mekhane/ochema/fake_extension_server.py",
    "mekhane/ochema/proto/__init__.py",
    "mekhane/ochema/proto/extension_server_pb2.py",
    "mekhane/ochema/proto/extension_server_pb2_grpc.py",
]

# Heuristic category mapping
CATEGORY_MAP = {
    "dendron": "[L2/Quality]",
    "anamnesis": "[L3/Context]",
    "mcp": "[L2/Infra]",
    "periskope": "[L2/Search]",
    "ccl": "[L1/Language]",
    "basanos": "[L2/Test]",
    "exagoge": "[L2/IO]",
    "ochema": "[L2/Orchestrator]",
    "api": "[L2/API]",
    "tape": "[L2/Mekhane]",
}

def get_category(path):
    parts = path.split("/")
    for p in parts:
        if p in CATEGORY_MAP:
            return CATEGORY_MAP[p]
    return "[L2/Mekhane]"

def process_file(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if header already exists
    if lines and lines[0].startswith("# PROOF:"):
        print(f"Skipping {filepath} (already has header)")
        return

    category = get_category(filepath)
    # Default Theorem O2 (Boulēsis) if unknown
    proof_line = f"# PROOF: {category} <- {filepath} O2→Intent→File"

    # Insert after shebang if present
    if lines and lines[0].startswith("#!"):
        new_lines = [lines[0], proof_line] + lines[1:]
    else:
        new_lines = [proof_line] + lines

    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"Updated {filepath}")

def main():
    for f in FILES:
        process_file(f)

if __name__ == "__main__":
    main()
