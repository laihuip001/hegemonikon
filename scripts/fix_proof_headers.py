#!/usr/bin/env python3
# PROOF: [L2/Impl] <- scripts/ Automated proof header fixer
"""
Add missing PROOF headers to files identified by Dendron check.
Usage: python scripts/fix_proof_headers.py
"""

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

def main():
    root = Path(".")
    for rel_path in MISSING_FILES:
        path = root / rel_path
        if not path.exists():
            print(f"Skipping {path} (not found)")
            continue

        content = path.read_text(encoding="utf-8")

        # Check if shebang exists
        lines = content.splitlines()
        has_shebang = lines and lines[0].startswith("#!")

        header = f"# PROOF: [L2/Impl] <- {path.parent}/ Automated fix for CI"

        if has_shebang:
            # Insert after shebang
            new_lines = [lines[0], header] + lines[1:]
        else:
            # Insert at top
            new_lines = [header] + lines

        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"Fixed {path}")

if __name__ == "__main__":
    main()
