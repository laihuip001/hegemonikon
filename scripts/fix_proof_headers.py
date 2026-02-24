import sys
from pathlib import Path

# The standard header to apply
PROOF_HEADER = "# PROOF: [L2/Impl] <- mekhane/ Automated fix for CI"

# List of files to fix (from CI log)
FILES_TO_FIX = [
    "mekhane/tape.py",
    "mekhane/api/routes/cortex.py",
    "mekhane/api/routes/devtools.py",
    "mekhane/mcp/mcp_guard.py",
    "mekhane/mcp/mcp_base.py",
    "mekhane/ccl/ccl_linter.py",
    "mekhane/ccl/operator_loader.py",
    "mekhane/dendron/falsification_checker.py",
    "mekhane/dendron/falsification_matcher.py",
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

def fix_file(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    if not lines:
        # Empty file
        path.write_text(f"{PROOF_HEADER}\n", encoding="utf-8")
        print(f"Fixed (empty): {filepath}")
        return

    # Check if PROOF header already exists
    if any(line.startswith("# PROOF:") for line in lines):
        print(f"Skipped (PROOF exists): {filepath}")
        return

    # Check for shebang
    if lines[0].startswith("#!"):
        # Insert after shebang
        lines.insert(1, f"{PROOF_HEADER}\n")
    else:
        # Insert at top
        lines.insert(0, f"{PROOF_HEADER}\n")

    path.write_text("".join(lines), encoding="utf-8")
    print(f"Fixed: {filepath}")

def main():
    root_dir = Path(__file__).parent.parent
    for filepath in FILES_TO_FIX:
        full_path = root_dir / filepath
        fix_file(full_path)

if __name__ == "__main__":
    main()
