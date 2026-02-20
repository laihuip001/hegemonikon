import os
from pathlib import Path

FILES = [
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

def add_proof_header(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    if content.startswith("# PROOF:"):
        print(f"Skipping {filepath} (already has header)")
        return

    # Determine category based on path
    if "mekhane/basanos" in filepath:
        header = f"# PROOF: [L2/Mekhanē] <- mekhane/basanos/"
    elif "mekhane/periskope" in filepath:
        header = f"# PROOF: [S2/Mekhanē] <- mekhane/periskope/"
    elif "mekhane/ochema" in filepath:
        header = f"# PROOF: [L2/Infrastructure] <- mekhane/ochema/"
    elif "mekhane/mcp" in filepath:
        header = f"# PROOF: [L2/Infrastructure] <- mekhane/mcp/"
    elif "mekhane/ccl" in filepath:
        header = f"# PROOF: [S1/Hermēneia] <- mekhane/ccl/"
    elif "mekhane/dendron" in filepath:
        header = f"# PROOF: [L2/Infrastructure] <- mekhane/dendron/"
    elif "mekhane/symploke" in filepath:
        header = f"# PROOF: [L2/Infrastructure] <- mekhane/symploke/"
    else:
        header = f"# PROOF: [L2/Mekhanē] <- {os.path.dirname(filepath)}/"

    new_content = f"{header}\n{content}"
    path.write_text(new_content, encoding="utf-8")
    print(f"Added header to {filepath}")

if __name__ == "__main__":
    for f in FILES:
        add_proof_header(f)
