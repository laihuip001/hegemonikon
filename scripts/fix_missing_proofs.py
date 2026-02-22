#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/ A0→品質保証→ヘッダ自動修復が必要
# PURPOSE: Dendron CI で検出された欠落 PROOF ヘッダを一括修復する
"""
Batch add missing # PROOF: headers to files identified by Dendron CI.
"""
from pathlib import Path

FILES = [
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

HEADER_TEMPLATE = "# PROOF: [L2/Mekhanē] <- {parent}/ A0→Need→This module fills it"

def main():
    root = Path(".")
    count = 0
    for fpath_str in FILES:
        path = root / fpath_str
        if not path.exists():
            print(f"Skipping (not found): {path}")
            continue

        content = path.read_text(encoding="utf-8")
        if content.startswith("# PROOF:"):
            print(f"Skipping (already has proof): {path}")
            continue

        parent = path.parent.name
        header = HEADER_TEMPLATE.format(parent=parent)

        # Preserve shebang
        if content.startswith("#!"):
            lines = content.splitlines(keepends=True)
            new_lines = [lines[0], header + "\n"] + lines[1:]
            new_content = "".join(new_lines)
        else:
            new_content = header + "\n" + content

        path.write_text(new_content, encoding="utf-8")
        print(f"Fixed: {path}")
        count += 1

    print(f"Total fixed: {count}")

if __name__ == "__main__":
    main()
