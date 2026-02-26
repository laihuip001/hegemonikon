
import os
import sys
from pathlib import Path

def add_proof_header(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {path}: not found")
        return

    content = path.read_text(encoding="utf-8")
    if content.startswith("# PROOF:"):
        print(f"Skipping {path}: already has PROOF")
        return

    # Determine parent directory for the proof string
    parent = path.parent.name

    # Construct the header
    header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI\n"

    # Add to content
    if content.startswith("#!"):
        # Preserve shebang
        lines = content.splitlines(keepends=True)
        lines.insert(1, header)
        new_content = "".join(lines)
    else:
        new_content = header + content

    path.write_text(new_content, encoding="utf-8")
    print(f"Fixed {path}")

def main():
    # List of files from the CI failure log
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
        "mekhane/ochema/proto/extension_server_pb2_grpc.py",
    ]

    for rel_path in missing_files:
        add_proof_header(rel_path)

if __name__ == "__main__":
    main()
