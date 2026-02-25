import os
from pathlib import Path

# List of files reported as missing PROOF headers in CI
files_missing_proof = [
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

def get_proof_header(filepath: str) -> str:
    """Determine the appropriate PROOF header based on the file path."""
    path = Path(filepath)

    # Generic fallback
    layer = "L2/Mekhane"
    coord = "A0"
    reason = "Existence"

    # Specific rules based on directory/path
    if "api/routes" in filepath:
        coord = "S2"
        reason = "API Route"
    elif "mcp/" in filepath:
        coord = "S2"
        reason = "MCP Server"
    elif "ccl/" in filepath:
        coord = "S1"
        reason = "CCL Component"
    elif "dendron/" in filepath:
        coord = "A2" # Krisis (Judgment/Validation)
        reason = "Quality Check"
    elif "symploke/" in filepath:
        coord = "S2"
        reason = "Specialist Integration"
    elif "periskope/" in filepath:
        coord = "S2"
        reason = "Search Engine"
    elif "basanos/" in filepath:
        layer = "L2/Basanos"
        coord = "A2" # Krisis
        reason = "Test/Validation"
    elif "ochema/" in filepath:
        coord = "S2"
        reason = "LLM Routing"
    elif "anamnesis/" in filepath:
        coord = "K3" # Anamnesis (Recollection)
        reason = "Memory/Embedding"
    elif "exagoge/" in filepath:
        coord = "S4" # Praxis
        reason = "Export/Action"

    # Construct the header line
    # Format: # PROOF: [Layer] <- path/ Coordinate->Reason
    # The path in the header typically points to the module root or specific file
    # For simplicity, we'll use the file's parent directory relative to repo root
    parent_dir = str(path.parent) + "/"
    if parent_dir == "./": parent_dir = ""

    return f"# PROOF: [{layer}] <- {filepath} {coord}->{reason}\n"

def fix_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping missing file: {filepath}")
        return

    content = path.read_text(encoding="utf-8")

    # Check if PROOF header already exists (simple check)
    if content.startswith("# PROOF:"):
        print(f"Skipping {filepath} (PROOF header exists)")
        return

    # Special handling for shebangs
    lines = content.splitlines(keepends=True)
    header = get_proof_header(filepath)

    new_lines = []
    if lines and lines[0].startswith("#!"):
        new_lines.append(lines[0])
        new_lines.append(header)
        new_lines.extend(lines[1:])
    else:
        new_lines.append(header)
        new_lines.extend(lines)

    path.write_text("".join(new_lines), encoding="utf-8")
    print(f"Fixed {filepath}")

def main():
    print(f"Fixing PROOF headers for {len(files_missing_proof)} files...")
    for filepath in files_missing_proof:
        try:
            fix_file(filepath)
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")

if __name__ == "__main__":
    main()
