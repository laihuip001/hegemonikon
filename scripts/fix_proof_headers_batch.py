import sys
from pathlib import Path

# PURPOSE: Inject missing PROOF headers into files
# Usage: python scripts/fix_proof_headers_batch.py

# List of files from the CI failure log
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

def main() -> None:
    for file_path in MISSING_FILES:
        path = Path(file_path)
        if not path.exists():
            print(f"Skipping missing file: {path}")
            continue

        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Check if header already exists (basic check)
        if any(line.startswith("# PROOF:") for line in lines[:5]):
            print(f"Skipping {path}: Header already present")
            continue

        # Determine parent dir for context
        parent_dir = path.parent.name
        header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent_dir}/ A0->Auto->AddedByCI"

        # Preserve shebang
        new_lines = []
        if lines and lines[0].startswith("#!"):
            new_lines.append(lines[0])
            new_lines.append(header)
            new_lines.extend(lines[1:])
        else:
            new_lines.append(header)
            new_lines.extend(lines)

        # Ensure newline at EOF
        new_content = "\n".join(new_lines) + "\n"
        path.write_text(new_content, encoding="utf-8")
        print(f"Fixed: {path}")

if __name__ == "__main__":
    main()
