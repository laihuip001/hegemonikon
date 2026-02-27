#!/usr/bin/env python3
# PROOF: [L2/ツール] <- scripts/fix_proofs_from_list.py
# PURPOSE: CIログから抽出した PROOF ヘッダ欠損ファイルに一括でヘッダを追加する
"""
Fix missing PROOF headers for files listed in CI failure logs.
"""
import sys
from pathlib import Path

# List of files from CI log
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
    # "mekhane/symploke/intent_wal.py", # Already fixed
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

def get_category(path_str):
    if "dendron" in path_str:
        return "[L2/Quality]"
    if "symploke" in path_str:
        return "[L2/Infra]"
    if "basanos" in path_str:
        return "[L2/Test]"
    if "periskope" in path_str:
        return "[L2/Search]"
    if "ccl" in path_str:
        return "[L2/Lang]"
    if "api" in path_str:
        return "[L2/API]"
    if "ochema" in path_str:
        return "[L2/Ochema]"
    return "[L2/Mekhane]"

def process_file(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {path} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    if "# PROOF:" in content:
        print(f"Skipping {path} (already has PROOF)")
        return

    category = get_category(filepath)
    # Simple proof generation
    proof_line = f"# PROOF: {category} <- {filepath} Auto-generated existence proof"

    # Insert after shebang if present
    lines = content.splitlines(keepends=True)
    if lines and lines[0].startswith("#!"):
        lines.insert(1, proof_line + "\n")
    else:
        lines.insert(0, proof_line + "\n")

    path.write_text("".join(lines), encoding="utf-8")
    print(f"Fixed {path}")

def main():
    print(f"Fixing {len(MISSING_FILES)} files...")
    for f in MISSING_FILES:
        process_file(f)
    print("Done.")

if __name__ == "__main__":
    main()
