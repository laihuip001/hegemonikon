# PROOF: [L2/Mekhane] <- scripts/fix_missing_proofs.py
# PURPOSE: Fix missing PROOF headers in 41 files reported by Dendron CI
import sys
from pathlib import Path

MISSING_FILES = [
    "mekhane/tape.py",
    "mekhane/api/routes/cortex.py",
    "mekhane/api/routes/devtools.py",
    "mekhane/mcp/mcp_guard.py",
    "mekhane/mcp/mcp_base.py",
    "mekhane/ccl/ccl_linter.py",
    "mekhane/ccl/operator_loader.py",
    "mekhane/dendron/falsification_checker.py",
    "mekhane/dendron/falsification_matcher.py",
    "mekhane/symploke/intent_wal.py",
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

def add_proof(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    if "# PROOF:" in content:
        print(f"Skipping {filepath} (already has PROOF)")
        return

    # Determine L2 category
    category = "L2/Mekhane"
    if "dendron" in filepath:
        category = "L2/Dendron"
    elif "symploke" in filepath:
        category = "L2/Symploke"
    elif "ccl" in filepath:
        category = "L2/CCL"
    elif "periskope" in filepath:
        category = "L2/Periskope"
    elif "basanos" in filepath:
        category = "L2/Basanos"
    elif "ochema" in filepath:
        category = "L2/Ochema"
    elif "api" in filepath:
        category = "L2/API"
    elif "mcp" in filepath:
        category = "L2/MCP"
    elif "anamnesis" in filepath:
        category = "L2/Anamnesis"
    elif "exagoge" in filepath:
        category = "L2/Exagoge"

    # Insert header
    header = f"# PROOF: [{category}] <- {filepath}\n"

    # Handle shebang
    lines = content.splitlines(keepends=True)
    if lines and lines[0].startswith("#!"):
        new_content = lines[0] + header + "".join(lines[1:])
    else:
        new_content = header + content

    path.write_text(new_content, encoding="utf-8")
    print(f"Added PROOF header to {filepath}")

if __name__ == "__main__":
    for f in MISSING_FILES:
        add_proof(f)
