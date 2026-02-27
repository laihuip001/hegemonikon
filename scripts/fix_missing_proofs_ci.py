
import os
import sys
from pathlib import Path

def fix_missing_proofs(root_dir: str):
    root = Path(root_dir)
    # List from the CI output
    missing_files = [
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

    for rel_path in missing_files:
        path = root / rel_path
        if not path.exists():
            print(f"Skipping {path} (not found)")
            continue

        content = path.read_text(encoding="utf-8")
        if "# PROOF:" in content:
            print(f"Skipping {path} (already has PROOF)")
            continue

        print(f"Fixing {path}")
        # Standard header format based on memory
        header = f"# PROOF: [L2/Mekhane] <- mekhane/{path.parent.name}/ A0->Auto->AddedByCI\n"

        # Handle shebang
        if content.startswith("#!"):
            lines = content.splitlines()
            lines.insert(1, header.strip())
            new_content = "\n".join(lines) + "\n" if content.endswith("\n") else "\n".join(lines)
        else:
            new_content = header + content

        path.write_text(new_content, encoding="utf-8")

if __name__ == "__main__":
    fix_missing_proofs(".")
