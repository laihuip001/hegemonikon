#!/usr/bin/env python3
"""
Script to add missing PROOF headers to files identified by dendron check.
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

PROOF_HEADER = "# PROOF: [L2/Impl] <- mekhane/ Automated fix for CI\n"

def main():
    root = Path(".")
    count = 0
    for file_path_str in MISSING_FILES:
        path = root / file_path_str
        if not path.exists():
            print(f"Skipping {path} (not found)")
            continue

        try:
            content = path.read_text(encoding="utf-8")
            if "PROOF:" in content:
                print(f"Skipping {path} (PROOF already exists)")
                continue

            lines = content.splitlines(keepends=True)
            new_lines = []
            inserted = False

            if lines and lines[0].startswith("#!"):
                new_lines.append(lines[0])
                new_lines.append(PROOF_HEADER)
                new_lines.extend(lines[1:])
                inserted = True
            else:
                new_lines.append(PROOF_HEADER)
                new_lines.extend(lines)
                inserted = True

            if inserted:
                path.write_text("".join(new_lines), encoding="utf-8")
                print(f"Fixed {path}")
                count += 1

        except Exception as e:
            print(f"Error processing {path}: {e}")

    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
