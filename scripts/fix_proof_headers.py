#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/fix_proof_headers.py Axiom->Reason->Module
# PURPOSE: CI で指摘された PROOF ヘッダ不足を修正するスクリプト

import os
from pathlib import Path

# CI ログから抽出したファイルリスト
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

def add_header(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if header already exists
    for line in lines[:5]:
        if line.startswith("# PROOF:"):
            print(f"Skipping {filepath} (header exists)")
            return

    # Create header
    # Category mapping heuristic
    category = "L2/Mekhane"
    if "basanos" in filepath:
        category = "L2/Basanos"
    elif "periskope" in filepath:
        category = "L2/Periskope"
    elif "ochema" in filepath:
        category = "L2/Ochema"

    header = f"# PROOF: [{category}] <- {filepath} Axiom->Reason->Module"

    new_lines = []
    if lines and lines[0].startswith("#!"):
        new_lines.append(lines[0])
        new_lines.append(header)
        new_lines.extend(lines[1:])
    else:
        new_lines.append(header)
        new_lines.extend(lines)

    # Ensure newline at end
    new_content = "\n".join(new_lines) + "\n"
    path.write_text(new_content, encoding="utf-8")
    print(f"Fixed {filepath}")

def main():
    print(f"Fixing {len(MISSING_FILES)} files...")
    for f in MISSING_FILES:
        add_header(f)
    print("Done.")

if __name__ == "__main__":
    main()
