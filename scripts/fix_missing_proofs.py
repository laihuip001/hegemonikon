#!/usr/bin/env python3
"""
Batch fix for missing PROOF headers.
Adds a default PROOF header to files listed in the CI error log.
"""

from pathlib import Path

MISSING_FILES = [
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

def fix_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    if "# PROOF:" in content:
        print(f"Skipping {filepath} (PROOF already exists)")
        return

    # Determine default PROOF based on directory
    if "api/routes" in filepath:
        proof = "# PROOF: [L2/インフラ] <- mekhane/api/routes/ A0→APIエンドポイント"
    elif "mcp" in filepath:
        proof = "# PROOF: [L2/インフラ] <- mekhane/mcp/ A0→MCP統合"
    elif "ccl" in filepath:
        proof = "# PROOF: [L1/定理] <- mekhane/ccl/ S1→CCL処理"
    elif "dendron" in filepath:
        proof = "# PROOF: [L2/品質] <- mekhane/dendron/ A4→品質保証"
    elif "periskope" in filepath:
        proof = "# PROOF: [L2/検索] <- mekhane/periskope/ K4→検索統合"
    elif "basanos" in filepath:
        proof = "# PROOF: [L2/検証] <- mekhane/basanos/ A2→検証基盤"
    elif "ochema" in filepath:
        proof = "# PROOF: [L2/基盤] <- mekhane/ochema/ S2→LLM統合"
    elif "anamnesis" in filepath:
        proof = "# PROOF: [L3/記憶] <- mekhane/anamnesis/ K3→記憶埋め込み"
    else:
        proof = f"# PROOF: [L2/Mekhane] <- {path.parent}/ A0→存在証明"

    # Prepend shebang if missing, otherwise insert after shebang
    lines = content.splitlines()
    if lines and lines[0].startswith("#!"):
        lines.insert(1, proof)
    else:
        lines.insert(0, proof)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Fixed {filepath}")

def main():
    print(f"Fixing {len(MISSING_FILES)} files...")
    for f in MISSING_FILES:
        fix_file(f)
    print("Done.")

if __name__ == "__main__":
    main()
