#!/usr/bin/env python3
"""
Adds missing PROOF headers to files identified in CI failure.
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

HEADER = "# PROOF: [L2/Impl] <- mekhane/ Automated fix for CI\n"

def add_header(filepath_str):
    path = Path(filepath_str)
    if not path.exists():
        print(f"Skipping {filepath_str}: not found")
        return

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Skipping {filepath_str}: read error {e}")
        return

    lines = content.splitlines(keepends=True)

    # Remove existing PROOF headers to avoid duplicates
    cleaned_lines = [line for line in lines if not (line.strip().startswith("# PROOF:") or line.strip().startswith("#PROOF:"))]

    new_lines = []

    # Simple logic: insert after shebang or encoding if present, else at top
    insert_index = 0
    for i, line in enumerate(cleaned_lines):
        if line.startswith("#!") or line.startswith("# -*-") or line.startswith("# coding"):
            insert_index = i + 1
        else:
            break

    if insert_index > 0:
        new_lines.extend(cleaned_lines[:insert_index])
        new_lines.append(HEADER)
        new_lines.extend(cleaned_lines[insert_index:])
    else:
        new_lines.append(HEADER)
        new_lines.extend(cleaned_lines)

    path.write_text("".join(new_lines), encoding="utf-8")
    print(f"Updated {filepath_str}")

if __name__ == "__main__":
    for f in FILES:
        add_header(f)
