#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/ A0→Utility→fix_missing_proof_headers.py
# PURPOSE: 自動化されたPROOFヘッダー修復によるCI安定化
"""
Batch add missing # PROOF headers to Python files.
"""
import sys
from pathlib import Path

def fix_file(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Skip if already has PROOF
    if any(line.startswith("# PROOF:") for line in lines[:5]):
        return

    # Determine insertion point (after shebang/encoding)
    insert_idx = 0
    if lines and (lines[0].startswith("#!") or lines[0].startswith("# -*-")):
        insert_idx += 1
        if len(lines) > 1 and (lines[1].startswith("#!") or lines[1].startswith("# -*-")):
            insert_idx += 1

    # Construct header
    # # PROOF: [Category] <- {parent_dir}/ A0→Implementation→{module_name}
    category = "[L2/Mekhane]"
    if "kernel" in path.parts:
        category = "[L0/Kernel]"
    elif "hermeneus" in path.parts:
        category = "[L1/Hermeneus]"
    elif "scripts" in path.parts:
        category = "[L3/Utility]"

    parent_dir = path.parent.name
    if parent_dir == "":
        parent_dir = "root"

    module_name = path.name

    header = f"# PROOF: {category} <- {parent_dir}/ A0→Implementation→{module_name}"

    lines.insert(insert_idx, header)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Fixed: {path}")

def main() -> None:
    # List of files from CI failure
    files = [
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

    root = Path(".")
    for fpath in files:
        p = root / fpath
        if p.exists():
            fix_file(p)
        else:
            print(f"Skipping missing: {p}")

if __name__ == "__main__":
    main()
