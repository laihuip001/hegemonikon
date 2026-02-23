#!/usr/bin/env python3
# PROOF: [L3/Scripts] <- scripts/add_proof_headers.py A0->General->Maintenance
# PURPOSE: Bulk add missing PROOF headers to files identified by CI.
"""
Bulk add missing PROOF headers to files identified by CI.
"""

import os
from pathlib import Path

FILES = [
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

def add_proof(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF already exists
    for line in lines:
        if line.startswith("# PROOF:"):
            print(f"Skipping {filepath} (PROOF exists)")
            return

    # Determine insertion point (after shebang/encoding)
    insert_idx = 0
    if lines and lines[0].startswith("#!"):
        insert_idx += 1
    if len(lines) > insert_idx and (lines[insert_idx].startswith("# -*-") or "coding:" in lines[insert_idx]):
        insert_idx += 1

    # Construct PROOF header
    # Format: # PROOF: [L2/Category] <- filepath A0->Chain->Module
    # Use ASCII arrows per memory guidelines
    filename = path.name
    category = "Mekhane"
    if "periskope" in filepath: category = "Periskope"
    if "basanos" in filepath: category = "Basanos"
    if "ochema" in filepath: category = "Ochema"
    if "dendron" in filepath: category = "Dendron"

    proof_line = f"# PROOF: [L2/{category}] <- {filepath} A0->General->{filename}"

    lines.insert(insert_idx, proof_line)

    # Write back
    new_content = "\n".join(lines) + "\n" # Ensure trailing newline
    path.write_text(new_content, encoding="utf-8")
    print(f"Updated {filepath}")

if __name__ == "__main__":
    for f in FILES:
        add_proof(f)
