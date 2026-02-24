#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/fix_proof_headers.py A0->Quality->Fix
# PURPOSE: Missing PROOF headers の自動修正
"""
Dendron CI で検出された Missing PROOF headers を自動修復する。
"""
import sys
from pathlib import Path

# Files identified by CI check
TARGETS = [
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

HEADER = "# PROOF: [L2/Mekhane] <- mekhane/dendron/ A0->Quality->Guard"

def fix_file(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    if not lines:
        new_content = HEADER + "\n"
    elif lines[0].startswith("#!"):
        # Insert after shebang
        new_content = lines[0] + "\n" + HEADER + "\n" + "\n".join(lines[1:]) + "\n"
    elif lines[0].startswith("# PROOF:"):
        print(f"Skipping {filepath} (already has header)")
        return
    else:
        new_content = HEADER + "\n" + content

    path.write_text(new_content, encoding="utf-8")
    print(f"Fixed {filepath}")

def main():
    root = Path(__file__).parent.parent
    for t in TARGETS:
        fix_file(root / t)

if __name__ == "__main__":
    main()
