#!/usr/bin/env python3
"""
Fix missing PROOF headers for 41 files identified in CI.
"""
import os
import sys
from pathlib import Path

MISSING_FILES = [
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
    "mekhane/basanos/l2/cli.py"
]

def add_proof_header(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    content = path.read_text(encoding="utf-8").splitlines()

    # Check if PROOF already exists
    for line in content[:10]:
        if line.startswith("# PROOF:"):
            print(f"Skipping {filepath} (PROOF exists)")
            return

    # Determine insertion point
    insert_idx = 0
    if content and content[0].startswith("#!"):
        insert_idx += 1
    if content and len(content) > insert_idx and (content[insert_idx].startswith("# -*-") or "coding:" in content[insert_idx]):
        insert_idx += 1

    filename = path.name
    parent = path.parent.name
    proof_line = f"# PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0→Implementation→{filename}"

    content.insert(insert_idx, proof_line)

    path.write_text("\n".join(content) + "\n", encoding="utf-8")
    print(f"✅ Added PROOF to {filepath}")

def main():
    print(f"Fixing {len(MISSING_FILES)} files...")
    for f in MISSING_FILES:
        add_proof_header(f)
    print("Done.")

if __name__ == "__main__":
    main()
