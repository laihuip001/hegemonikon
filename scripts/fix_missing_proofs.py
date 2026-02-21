import os
from pathlib import Path

# List of files identified in the CI failure log
files_to_fix = [
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
    "mekhane/exagoge/__main__.py"
]

def add_proof_header(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF header already exists
    if any(line.startswith("# PROOF:") for line in lines[:5]):
        print(f"Skipping {filepath} (PROOF header exists)")
        return

    # Determine header content
    # Format: # PROOF: [L2/Category] <- path/to/module
    # We'll use a generic [L2/Mekhane] for simplicity, or try to infer category
    category = "Mekhane"
    if "periskope" in filepath:
        category = "Periskope"
    elif "basanos" in filepath:
        category = "Basanos"
    elif "dendron" in filepath:
        category = "Dendron"
    elif "ochema" in filepath:
        category = "Ochema"
    elif "ccl" in filepath:
        category = "CCL"

    header = f"# PROOF: [L2/{category}] <- {filepath}"

    # Insert header
    new_lines = []
    inserted = False

    # Handle shebang
    if lines and lines[0].startswith("#!"):
        new_lines.append(lines[0])
        new_lines.append(header)
        new_lines.extend(lines[1:])
        inserted = True
    else:
        new_lines.append(header)
        new_lines.extend(lines)
        inserted = True

    if inserted:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"Fixed {filepath}")

if __name__ == "__main__":
    for f in files_to_fix:
        add_proof_header(f)
