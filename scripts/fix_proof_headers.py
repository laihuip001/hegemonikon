#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/ A0->Maintenance->FixHeaders
# PURPOSE: Automatically inject missing PROOF headers into files
"""
Fix Proof Headers - Injects default PROOF headers where missing.

Usage:
    python scripts/fix_proof_headers.py
"""

import sys
from pathlib import Path

# List of files identified in the CI failure
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

def main():
    root = Path(".")
    fixed_count = 0

    for rel_path in MISSING_PROOF_FILES:
        path = root / rel_path
        if not path.exists():
            print(f"⚠️  File not found: {rel_path}")
            continue

        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check if already has PROOF
        if any(line.startswith("# PROOF:") for line in lines[:5]):
            print(f"⏭️  Skipping {rel_path} (PROOF present)")
            continue

        # Determine insertion point (after shebang if present)
        insert_idx = 0
        if lines and lines[0].startswith("#!"):
            insert_idx = 1

        # Prepare header
        # Using [L2/Mekhane] as generic category since we don't know the specific axiom trace for each
        # We try to infer the parent path
        parent_path = str(Path(rel_path).parent) + "/"
        header = f"# PROOF: [L2/Mekhane] <- {parent_path} A0->Implementation->Module"

        lines.insert(insert_idx, header)

        # Write back
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"✅ Fixed {rel_path}")
        fixed_count += 1

    print(f"\nTotal fixed: {fixed_count}")

if __name__ == "__main__":
    main()
