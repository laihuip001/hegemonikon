#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/
# PURPOSE: CI で不足している PROOF ヘッダーを自動付与する
"""
Fix missing PROOF headers for CI.

Injects: # PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI
"""
import sys
from pathlib import Path

# List of files identified in CI failure
MISSING_FILES = [
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
    "mekhane/symploke/intent_wal.py",
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

def fix_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping missing file: {filepath}")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF already exists
    for line in lines[:5]:
        if line.startswith("# PROOF:"):
            print(f"Skipping {filepath}: Already has PROOF header")
            return

    # Prepare header
    parent_dir = path.parent.name
    header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent_dir}/ A0->Auto->AddedByCI"

    new_lines = []
    inserted = False

    # Handle shebang
    if lines and lines[0].startswith("#!"):
        new_lines.append(lines[0])
        new_lines.append(header)
        new_lines.extend(lines[1:])
        inserted = True
    else:
        new_lines.append(header)
        new_lines.extend(lines)
        inserted = True

    if inserted:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"Fixed {filepath}")

def main():
    print(f"Fixing {len(MISSING_FILES)} files...")
    for f in MISSING_FILES:
        fix_file(f)
    print("Done.")

if __name__ == "__main__":
    main()
