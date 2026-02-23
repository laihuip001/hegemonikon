#!/usr/bin/env python3
"""
Helper script to fix missing PROOF headers identified by CI.
Usage: python scripts/fix_proof_headers.py
"""

import os
from pathlib import Path

# List of files identified in the CI failure log
MISSING_PROOF_FILES = [
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

def fix_proof_header(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"⚠️ File not found: {filepath}")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF header already exists
    for line in lines[:5]:
        if line.startswith("# PROOF:"):
            print(f"✅ PROOF header already exists in {filepath}")
            return

    # Determine class/module name for the PROOF trace
    name = path.stem.replace("_", " ").title().replace(" ", "")

    # Generic PROOF header
    # Using ASCII arrow '->' to avoid Unicode issues in CI checks
    proof_header = f"# PROOF: [L2/Mekhane] <- {filepath} O1->Zet->{name}"

    # Insert after shebang if present, otherwise at the top
    if lines and lines[0].startswith("#!"):
        lines.insert(1, proof_header)
    else:
        lines.insert(0, proof_header)

    new_content = "\n".join(lines) + "\n"
    path.write_text(new_content, encoding="utf-8")
    print(f"🛠️ Added PROOF header to {filepath}")

def main():
    print(f"🔍 Checking {len(MISSING_PROOF_FILES)} files for missing PROOF headers...")
    for filepath in MISSING_PROOF_FILES:
        fix_proof_header(filepath)
    print("✨ Done.")

if __name__ == "__main__":
    main()
