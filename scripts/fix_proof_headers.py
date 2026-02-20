
import os
from pathlib import Path

FILES = [
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

MAPPINGS = [
    ("mekhane/periskope/", "# PROOF: [L2/Mekhane] <- mekhane/periskope/ A0->Discovery->Periskope searches external knowledge"),
    ("mekhane/tape.py", "# PROOF: [L2/Mekhane] <- mekhane/ A0->Recording->Tape records operations"),
    ("mekhane/api/routes/", "# PROOF: [L2/Interface] <- mekhane/api/ A0->Communication->API routes"),
    ("mekhane/mcp/", "# PROOF: [L2/Interface] <- mekhane/mcp/ A0->Integration->MCP protocol implementation"),
    ("mekhane/ccl/", "# PROOF: [L2/Mekhane] <- mekhane/ccl/ A0->Cognition->CCL interpretation"),
    ("mekhane/dendron/", "# PROOF: [L2/System] <- mekhane/dendron/ A0->Structure->Dendron verifies structural integrity"),
    ("mekhane/symploke/", "# PROOF: [L2/System] <- mekhane/symploke/ A0->Feedback->Symploke integration"),
    ("mekhane/basanos/", "# PROOF: [L2/Verification] <- mekhane/basanos/ A0->Testing->Basanos verifies logic"),
    ("mekhane/ochema/", "# PROOF: [L2/Mekhane] <- mekhane/ochema/ A0->Routing->Ochema routes requests"),
    ("mekhane/anamnesis/", "# PROOF: [L2/Mekhane] <- mekhane/anamnesis/ A0->Memory->Anamnesis recalls knowledge"),
    ("mekhane/exagoge/", "# PROOF: [L2/Mekhane] <- mekhane/exagoge/ A0->Export->Exagoge exports data"),
]

def get_proof(path):
    for prefix, proof in MAPPINGS:
        if path.startswith(prefix):
            return proof
    return "# PROOF: [L2/Mekhane] <- mekhane/ A0->Implementation->Module implementation"

def fix_file(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"Skipping {filepath} (binary or encoding error)")
        return

    if content.startswith("# PROOF:"):
        print(f"Skipping {filepath} (already has proof)")
        return

    proof = get_proof(filepath)

    # Handle shebang
    lines = content.splitlines(keepends=True)
    if lines and lines[0].startswith("#!"):
        new_content = lines[0] + proof + "\n" + "".join(lines[1:])
    else:
        new_content = proof + "\n" + content

    path.write_text(new_content, encoding="utf-8")
    print(f"Fixed {filepath}")

for f in FILES:
    fix_file(f)
