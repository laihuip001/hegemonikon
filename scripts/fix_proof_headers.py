# PURPOSE: Add missing PROOF headers to files identified by Dendron CI
import sys
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

def add_proof_header(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping missing file: {filepath}")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF already exists
    for line in lines[:5]:
        if line.startswith("# PROOF:"):
            print(f"Skipping {filepath}: PROOF header already exists")
            return

    class_name = path.stem.title().replace("_", "")
    header = f"# PROOF: [L2/Mekhane] <- {filepath} O1->Zet->{class_name}"

    # Insert after shebang/encoding if present
    insert_idx = 0
    if lines and (lines[0].startswith("#!") or lines[0].startswith("# -*-")):
        insert_idx += 1
        if len(lines) > 1 and (lines[1].startswith("#!") or lines[1].startswith("# -*-")):
            insert_idx += 1

    lines.insert(insert_idx, header)

    # Ensure newline after header if needed
    # (Checking if next line is docstring or import)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Added PROOF header to {filepath}")

def main():
    print(f"Processing {len(MISSING_FILES)} files...")
    for f in MISSING_FILES:
        add_proof_header(f)
    print("Done.")

if __name__ == "__main__":
    main()
