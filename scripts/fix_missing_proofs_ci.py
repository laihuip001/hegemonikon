#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/
# PURPOSE: CI検証用の一括 PROOF ヘッダ注入スクリプト
"""
CI Missing Proof Fixer

Fixes missing # PROOF: headers detected by Dendron validation in CI.
"""
import argparse
from pathlib import Path

# Fix targets from CI failure log
# Note: hermeneus/src/prover.py is excluded as it was fixed manually/verified
TARGETS = [
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def fix_file(filepath: Path):
    if not filepath.exists():
        print(f"Skipping (not found): {filepath}")
        return

    content = filepath.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF header already exists
    if lines and lines[0].startswith("# PROOF:"):
        print(f"Skipping (already has PROOF): {filepath}")
        return

    # Determine PROOF header content
    # Heuristic: [L2/Mekhane] or [L3/Integration] based on path
    parent_dir = filepath.parent.name
    grandparent_dir = filepath.parent.parent.name

    layer = "L2"
    category = "Mekhane"

    if "scripts" in filepath.parts:
        layer = "L3"
        category = "ユーティリティ"
    elif "periskope" in filepath.parts:
        layer = "L2"
        category = "検索"
    elif "dendron" in filepath.parts:
        layer = "L2"
        category = "品質"
    elif "basanos" in filepath.parts:
        layer = "L2"
        category = "評価"
    elif "ochema" in filepath.parts:
        layer = "L2"
        category = "ルーティング"
    elif "ccl" in filepath.parts:
        layer = "L2"
        category = "言語"

    proof_line = f"# PROOF: [{layer}/{category}] <- {filepath.parent.relative_to(PROJECT_ROOT)}/ A0->Auto->AddedByCI"

    # Insert at top (preserving shebang if present)
    if lines and lines[0].startswith("#!"):
        lines.insert(1, proof_line)
    else:
        lines.insert(0, proof_line)

    filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ Fixed: {filepath}")

def main():
    print(f" fixing {len(TARGETS)} missing proofs...")
    for target in TARGETS:
        fix_file(PROJECT_ROOT / target)

if __name__ == "__main__":
    main()
