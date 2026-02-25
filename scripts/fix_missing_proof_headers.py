#!/usr/bin/env python3
"""
Batch fix missing PROOF headers in Python files.
Requires a list of files as arguments.
"""

import sys
import re
from pathlib import Path

PROOF_TEMPLATE = '# PROOF: [L2/Mekhane] <- {parent_dir}/ A0→Implementation→{module_name}\n'

def fix_file(filepath: Path):
    if not filepath.exists():
        print(f"Skipping {filepath}: File not found")
        return

    content = filepath.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF header already exists
    if any(line.startswith("# PROOF:") for line in lines[:5]):
        print(f"Skipping {filepath}: PROOF header already exists")
        return

    parent_dir = filepath.parent.name
    module_name = filepath.stem
    proof_header = PROOF_TEMPLATE.format(parent_dir=parent_dir, module_name=module_name)

    # Insert after shebang or encoding cookie, or at top
    insert_idx = 0
    if lines and lines[0].startswith("#!"):
        insert_idx = 1
        if len(lines) > 1 and "coding" in lines[1]:
            insert_idx = 2
    elif lines and "coding" in lines[0]:
        insert_idx = 1

    lines.insert(insert_idx, proof_header.strip())

    filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Fixed {filepath}")

def main():
    files = [
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

    for f in files:
        fix_file(Path(f))

if __name__ == "__main__":
    main()
