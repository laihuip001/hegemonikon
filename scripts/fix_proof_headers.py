#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/ A0→DevOps→fix_proof_headers
# PURPOSE: 欠損している # PROOF: ヘッダを自動追記する (Dendron CI 対応)
"""
Fix missing PROOF headers in Python files.
Usage: python scripts/fix_proof_headers.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Files identified from CI failure log
TARGET_FILES = [
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

def add_proof_header(filepath: str):
    """Add default PROOF header to file."""
    path = PROJECT_ROOT / filepath
    if not path.exists():
        print(f"Skipping {filepath}: File not found")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF already exists (double check)
    for i, line in enumerate(lines[:5]):
        if line.strip().startswith("# PROOF:"):
            print(f"Skipping {filepath}: PROOF header already exists at line {i+1}")
            return

    # Construct header
    # Format: # PROOF: [L2/Mekhane] <- {parent}/ A0→Implementation→{module}
    parent_dir = path.parent.name
    module_name = path.stem
    header = f"# PROOF: [L2/Mekhane] <- {parent_dir}/ A0→Implementation→{module_name}"

    # Insert header logic
    # 1. If line 1 is shebang, insert at line 2.
    # 2. Otherwise insert at line 1.

    new_lines = []

    if lines and lines[0].startswith("#!"):
        new_lines.append(lines[0])
        new_lines.append(header)
        new_lines.extend(lines[1:])
    else:
        new_lines.append(header)
        new_lines.extend(lines)

    # Write back
    # Ensure newline at end of file if it was there or if list is not empty
    final_content = "\n".join(new_lines) + "\n"
    path.write_text(final_content, encoding="utf-8")
    print(f"Fixed: {filepath}")

def main():
    print(f"Fixing {len(TARGET_FILES)} files identified from CI failure log...")
    for f in TARGET_FILES:
        add_proof_header(f)
    print("Done.")

if __name__ == "__main__":
    main()
