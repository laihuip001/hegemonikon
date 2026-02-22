#!/usr/bin/env python3
"""
Fix missing PROOF headers in Python files.
"""

import os

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

def fix_file(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Check if PROOF already exists
    for line in lines[:5]:  # Check first 5 lines
        if line.strip().startswith("# PROOF:"):
            print(f"Skipping {filepath} (PROOF found)")
            return

    # Determine insertion point
    insert_idx = 0
    if lines and lines[0].startswith("#!"):
        insert_idx = 1

    # Create PROOF header
    # Format: # PROOF: [L2/Mekhane] <- {path} FEP->Implementation
    proof_line = f"# PROOF: [L2/Mekhane] <- {filepath} FEP->Implementation\n"

    lines.insert(insert_idx, proof_line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Fixed {filepath}")

def main():
    print(f"Fixing {len(FILES_TO_FIX)} files...")
    for filepath in FILES_TO_FIX:
        fix_file(filepath)
    print("Done.")

if __name__ == "__main__":
    main()
