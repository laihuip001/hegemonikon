import os
import sys

# List of files identified by dendron check
missing_files = [
    "mekhane/tape.py",
    "mekhane/ccl/operator_loader.py",
    "mekhane/ccl/ccl_linter.py",
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

PROOF_TEMPLATE = "# PROOF: [L2/Mekhane] <- mekhane/ A0→Implementation→Module"

def add_proof_header(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Check if PROOF already exists
    for line in lines[:5]:
        if line.startswith("# PROOF:"):
            print(f"Skipping {filepath} (PROOF exists)")
            return

    # Determine insertion point (after shebang/encoding or at top)
    insert_idx = 0
    if lines and (lines[0].startswith("#!") or lines[0].startswith("# -*-")):
        insert_idx += 1
        if len(lines) > 1 and (lines[1].startswith("# -*-") or lines[1].startswith("#!") ):
             insert_idx += 1

    # Construct specific proof based on path
    specific_proof = PROOF_TEMPLATE
    if "periskope" in filepath:
        specific_proof = "# PROOF: [L2/Mekhane] <- mekhane/periskope/ P2→Search→Module"
    elif "basanos" in filepath:
        specific_proof = "# PROOF: [L2/Mekhane] <- mekhane/basanos/ A2→Test→Module"
    elif "dendron" in filepath:
        specific_proof = "# PROOF: [L2/Mekhane] <- mekhane/dendron/ A4→Quality→Module"

    # Insert
    lines.insert(insert_idx, specific_proof + "\n")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"Added PROOF to {filepath}")

if __name__ == "__main__":
    for f in missing_files:
        add_proof_header(f)
