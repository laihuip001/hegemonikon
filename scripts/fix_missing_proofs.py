#!/usr/bin/env python3
"""
Bulk fix for missing PROOF headers in Dendron check.
"""
from pathlib import Path

FILES = [
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

PROOF_TEMPLATE = "# PROOF: [L2/Mekhane] <- {}/ A0->Existence"

def fix_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping (not found): {filepath}")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF header already exists
    if any(line.startswith("# PROOF:") for line in lines):
        print(f"Skipping (already has PROOF): {filepath}")
        return

    # Determine insertion point
    insert_idx = 0
    if lines and lines[0].startswith("#!"):
        insert_idx = 1

    # Generate generic PROOF header based on parent directory
    parent_dir = path.parent.name
    proof_header = PROOF_TEMPLATE.format(parent_dir)

    lines.insert(insert_idx, proof_header)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Fixed: {filepath}")

def main():
    for f in FILES:
        fix_file(f)

if __name__ == "__main__":
    main()
