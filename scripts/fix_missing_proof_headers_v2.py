#!/usr/bin/env python3
# PROOF: [L2/ツール] <- scripts/fix_missing_proof_headers_v2.py
# PURPOSE: mekhane/ 以下の Python ファイルに不足している PROOF ヘッダを一括追加する
"""
Fix Missing PROOF Headers V2 - 暫定スクリプト

ci failure "PROOF Header Validation" に対応するため、
不足している 41 ファイルにヘッダを追加する。
"""

import sys
from pathlib import Path

MISSING_FILES = [
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

def get_category(path_str):
    if "dendron" in path_str: return "[L2/Quality]"
    if "symploke" in path_str: return "[L2/Infra]"
    if "basanos" in path_str: return "[L2/Test]"
    if "periskope" in path_str: return "[L2/Search]"
    if "ochema" in path_str: return "[L2/LLM]"
    if "mcp" in path_str: return "[L2/MCP]"
    if "ccl" in path_str: return "[L2/CCL]"
    if "api" in path_str: return "[L2/API]"
    return "[L2/Mekhane]"

def fix_file(path_str):
    p = Path(path_str)
    if not p.exists():
        print(f"Skipping (not found): {path_str}")
        return

    content = p.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Skip if already has PROOF
    if any(l.startswith("# PROOF:") for l in lines[:5]):
        print(f"Skipping (has PROOF): {path_str}")
        return

    category = get_category(path_str)
    # Default Theorem mapping based on path
    theorem = "A0" # Default existence

    header = f"# PROOF: {category} <- {path_str} {theorem}→AutoFix"

    # Insert at top, preserving shebang
    new_lines = []
    if lines and lines[0].startswith("#!"):
        new_lines.append(lines[0])
        new_lines.append(header)
        new_lines.extend(lines[1:])
    else:
        new_lines.append(header)
        new_lines.extend(lines)

    # Write back
    p.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"Fixed: {path_str}")

def main():
    for f in MISSING_FILES:
        fix_file(f)

if __name__ == "__main__":
    main()
