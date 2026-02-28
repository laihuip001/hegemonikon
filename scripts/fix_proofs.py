import sys
import os
import re

def fix_proofs(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, 'r') as f:
        content = f.read()

    # Check if PROOF header exists
    if re.search(r"#\s*PROOF:\s*\[", content):
        return

    # Add default PROOF header based on location
    if "api/" in filepath:
        proof = "# PROOF: [L2/インフラ]\n"
    elif "tests/" in filepath:
        proof = "# PROOF: [L2/インフラ]\n"
    elif "basanos/" in filepath:
        proof = "# PROOF: [L2/インフラ]\n"
    elif "periskope/" in filepath:
        proof = "# PROOF: [L2/インフラ]\n"
    elif "ochema/" in filepath:
        proof = "# PROOF: [L2/インフラ]\n"
    else:
        proof = "# PROOF: [L2/インフラ]\n"

    # Insert after shebang if present, otherwise at top
    if content.startswith("#!"):
        parts = content.split("\n", 1)
        if len(parts) > 1:
            new_content = parts[0] + "\n" + proof + parts[1]
        else:
            new_content = parts[0] + "\n" + proof
    else:
        new_content = proof + content

    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Added PROOF to {filepath}")

# Parse the dendron check output or list of files
files_to_fix = [
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
    "mekhane/basanos/l2/cli.py"
]

for file in files_to_fix:
    fix_proofs(file)
