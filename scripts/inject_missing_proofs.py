# PURPOSE: Batch inject missing PROOF headers based on CI failure log
# PROOF: [L2/Mekhane] <- scripts/ A0->Auto->FixMissingProofsCI

import os
from pathlib import Path

# Files listed in CI failure (41 files)
# Manually copied from the provided log
MISSING_FILES = [
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

def main():
    root = Path.cwd()
    count = 0
    for rel_path in MISSING_FILES:
        file_path = root / rel_path
        if not file_path.exists():
            print(f"Skipping {rel_path}: File not found")
            continue

        content = file_path.read_text(encoding="utf-8")
        if "# PROOF:" in content:
            print(f"Skipping {rel_path}: Header already present")
            continue

        # Determine parent for PROOF header context
        parts = rel_path.split("/")
        parent = parts[0] if len(parts) > 1 else "root"
        if len(parts) > 2:
             parent = f"{parts[0]}/{parts[1]}"

        # Inject header
        # [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI
        header = f"# PROOF: [L2/Mekhane] <- {parent}/ A0->Auto->AddedByCI\n"

        # If hashbang exists, put after hashbang
        lines = content.splitlines(keepends=True)
        if lines and lines[0].startswith("#!"):
            lines.insert(1, header)
        else:
            lines.insert(0, header)

        file_path.write_text("".join(lines), encoding="utf-8")
        print(f"Injected PROOF header to {rel_path}")
        count += 1

    print(f"Finished. Injected {count} headers.")

if __name__ == "__main__":
    main()
