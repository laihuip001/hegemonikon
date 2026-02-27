#!/usr/bin/env python3
# PURPOSE: Fix missing PROOF headers in Python files for CI
import os
import re
from pathlib import Path

def main():
    root = Path(".")
    missing_files = []

    # Run check to get list of files
    import subprocess
    try:
        # We can't trust the previous output because file paths might be relative
        # Let's just walk and check manually or use the CLI if possible.
        # But for this script, I'll implement a simple walker and checker
        # matching the Dendron behavior.
        pass
    except Exception:
        pass

    # Files listed in the CI failure log
    target_files = [
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
        "mekhane/ochema/proto/extension_server_pb2_grpc.py"
    ]

    for rel_path in target_files:
        path = root / rel_path
        if not path.exists():
            print(f"Skipping {path} (not found)")
            continue

        content = path.read_text(encoding="utf-8")

        # Check if PROOF header exists
        if re.search(r"^# PROOF:", content, re.MULTILINE):
            print(f"Skipping {path} (has PROOF)")
            continue

        print(f"Fixing {path}...")

        # Construct PROOF header
        # Format: # PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI
        parent = path.parent.name
        header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI\n"

        # Insert at top, preserving shebang if present
        lines = content.splitlines(keepends=True)
        if lines and lines[0].startswith("#!"):
            lines.insert(1, header)
        else:
            lines.insert(0, header)

        path.write_text("".join(lines), encoding="utf-8")

if __name__ == "__main__":
    main()
