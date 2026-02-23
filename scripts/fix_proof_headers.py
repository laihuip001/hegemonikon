#!/usr/bin/env python3
"""
Script to fix missing PROOF headers in files identified by CI.
"""

import os
from pathlib import Path

FILES_TO_FIX = [
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

def fix_proof_headers():
    project_root = Path.cwd()

    for rel_path in FILES_TO_FIX:
        file_path = project_root / rel_path
        if not file_path.exists():
            print(f"Skipping missing file: {rel_path}")
            continue

        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check if PROOF header exists
        has_proof = any(line.startswith("# PROOF:") for line in lines[:5])
        if has_proof:
            print(f"Skipping {rel_path} (PROOF header exists)")
            continue

        print(f"Fixing {rel_path}...")

        # Determine header content
        if "mekhane/symploke/intent_wal.py" in rel_path:
            header = "# PROOF: [L2/Mekhane] <- mekhane/symploke/intent_wal.py O1->Zet->IntentWAL"
        else:
            header = f"# PROOF: [L2/Mekhane] <- {rel_path} A0->Found->Fix"

        # Insert header
        # Special handling: insert after shebang or encoding cookie if present
        insert_idx = 0
        if lines and (lines[0].startswith("#!") or lines[0].startswith("# -*-")):
            insert_idx += 1
            if len(lines) > 1 and (lines[1].startswith("#!") or lines[1].startswith("# -*-")):
                insert_idx += 1

        # For deficit_factories.py, ensure it is the first semantic line (before PURPOSE if possible)
        # But generally PROOF should be top-level.

        lines.insert(insert_idx, header)

        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    fix_proof_headers()
