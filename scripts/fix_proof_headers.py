#!/usr/bin/env python3
# PROOF: [L3/Utilities] <- scripts/ A0→Maintenance→fix_proof_headers
# PURPOSE: Automatically add PROOF headers to files missing them to satisfy Dendron CI
"""
Fix missing PROOF headers in Python files.
"""
import sys
from pathlib import Path

def main():
    root = Path("mekhane")
    count = 0

    # Files identified from Dendron check report
    targets = [
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

    for t in targets:
        path = Path(t)
        if not path.exists():
            print(f"Skipping missing file: {t}")
            continue

        content = path.read_text(encoding="utf-8")
        if content.startswith("# PROOF:"):
            print(f"Skipping {t} (header exists)")
            continue

        # Determine module name for header
        module_name = path.stem
        parent_dir = path.parent

        # Construct header
        header = f"# PROOF: [L2/Mekhane] <- {parent_dir}/ A0→Implementation→{module_name}\n"

        # Handle shebang
        lines = content.splitlines(keepends=True)
        if lines and lines[0].startswith("#!"):
            lines.insert(1, header)
        else:
            lines.insert(0, header)

        path.write_text("".join(lines), encoding="utf-8")
        print(f"Fixed {t}")
        count += 1

    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
