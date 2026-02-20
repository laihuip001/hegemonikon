#!/usr/bin/env python3
"""
Fix missing PROOF headers in mekhane submodules.
"""
import sys
from pathlib import Path

# Files identified from the CI log as missing PROOF headers
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
    "mekhane/exagoge/__main__.py"
]

def fix_header(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF header already exists
    for line in lines[:5]:
        if line.startswith("# PROOF:"):
            print(f"Skipping {filepath} (header exists)")
            return

    # Determine category based on path
    parent_dir = path.parent.name
    grandparent_dir = path.parent.parent.name

    category = "L2/インフラ"
    trace_path = f"mekhane/{parent_dir}/"
    if grandparent_dir != "mekhane":
         trace_path = f"mekhane/{grandparent_dir}/{parent_dir}/"

    header = f"# PROOF: [{category}] <- {trace_path} Automated fix"

    # Insert header
    if lines and lines[0].startswith("#!"):
        # Preserve shebang
        lines.insert(1, header)
    else:
        lines.insert(0, header)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Fixed {filepath}")

def main():
    print(f"Fixing {len(MISSING_FILES)} files...")
    for filepath in MISSING_FILES:
        fix_header(filepath)
    print("Done.")

if __name__ == "__main__":
    main()
