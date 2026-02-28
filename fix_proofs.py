import os
import re

MISSING_PROOFS = [
    'mekhane/tape.py',
    'mekhane/ccl/operator_loader.py',
    'mekhane/ccl/ccl_linter.py',
    'mekhane/symploke/intent_wal.py',
    'mekhane/mcp/mcp_guard.py',
    'mekhane/mcp/mcp_base.py',
    'mekhane/ochema/ls_launcher.py',
    'mekhane/ochema/fake_extension_server.py',
    'mekhane/dendron/falsification_checker.py',
    'mekhane/dendron/falsification_matcher.py',
    'mekhane/periskope/engine.py',
    'mekhane/periskope/synthesizer.py',
    'mekhane/periskope/models.py',
    'mekhane/periskope/query_expander.py',
    'mekhane/periskope/__init__.py',
    'mekhane/periskope/citation_agent.py',
    'mekhane/periskope/page_fetcher.py',
    'mekhane/periskope/cli.py',
    'mekhane/exagoge/__main__.py',
    'mekhane/anamnesis/vertex_embedder.py',
    'mekhane/ochema/proto/extension_server_pb2_grpc.py',
    'mekhane/ochema/proto/__init__.py',
    'mekhane/ochema/proto/extension_server_pb2.py',
    'mekhane/periskope/searchers/__init__.py',
    'mekhane/periskope/searchers/internal_searcher.py',
    'mekhane/periskope/searchers/tavily_searcher.py',
    'mekhane/periskope/searchers/semantic_scholar_searcher.py',
    'mekhane/periskope/searchers/playwright_searcher.py',
    'mekhane/periskope/searchers/brave_searcher.py',
    'mekhane/periskope/searchers/searxng.py',
    'mekhane/api/routes/cortex.py',
    'mekhane/api/routes/devtools.py',
    'mekhane/basanos/l2/g_semantic.py',
    'mekhane/basanos/l2/resolver.py',
    'mekhane/basanos/l2/models.py',
    'mekhane/basanos/l2/g_struct.py',
    'mekhane/basanos/l2/__init__.py',
    'mekhane/basanos/l2/deficit_factories.py',
    'mekhane/basanos/l2/hom.py',
    'mekhane/basanos/l2/history.py',
    'mekhane/basanos/l2/cli.py'
]

def ensure_proof_header(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}: not found")
        return

    with open(filepath, 'r') as f:
        content = f.read()

    if "PROOF:" in content[:200]:
        print(f"Skipping {filepath}: PROOF already exists")
        return

    # Get level from filepath
    level = "L2/インフラ"
    if "/api/" in filepath or "/cli.py" in filepath or "/__main__.py" in filepath:
        level = "L3/機能"
    elif "/dendron/" in filepath or "/basanos/" in filepath or "/symploke/" in filepath:
        level = "L2/インフラ"

    header = f"# PROOF: [{level}] <- {os.path.dirname(filepath)}/\n"

    # Insert after shebang or at top
    if content.startswith("#!"):
        lines = content.split('\n', 1)
        new_content = f"{lines[0]}\n{header}{lines[1] if len(lines)>1 else ''}"
    else:
        new_content = header + content

    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Added PROOF header to {filepath}")

for f in MISSING_PROOFS:
    ensure_proof_header(f)
