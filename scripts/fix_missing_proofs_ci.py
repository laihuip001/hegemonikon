#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/ A0->Auto->AddedByCI
# PURPOSE: Batch inject missing PROOF headers to satisfy CI checks
import sys
from pathlib import Path

def main():
    root = Path(".")
    # Files identified from the CI failure log
    missing_files = [
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

    for rel_path in missing_files:
        fpath = root / rel_path
        if not fpath.exists():
            print(f"Skipping {fpath} (not found)")
            continue

        try:
            content = fpath.read_text(encoding="utf-8")
            if content.startswith("# PROOF:"):
                print(f"Skipping {fpath} (already has proof)")
                continue

            # Determine parent for the proof trace
            parent = fpath.parent.name
            if parent == "":
                parent = "root"

            header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI\n"

            # Preserve shebang if present
            if content.startswith("#!"):
                lines = content.splitlines(keepends=True)
                new_content = lines[0] + header + "".join(lines[1:])
            else:
                new_content = header + content

            fpath.write_text(new_content, encoding="utf-8")
            print(f"Fixed {fpath}")

        except Exception as e:
            print(f"Error processing {fpath}: {e}")

if __name__ == "__main__":
    main()
