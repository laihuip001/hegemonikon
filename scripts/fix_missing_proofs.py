#!/usr/bin/env python3
# PROOF: [L3/Utility] <- scripts/fix_missing_proofs.py
"""
Fix missing PROOF headers in specific files.
Handles shebang lines correctly by inserting the header after them.
Also fixes files where the header was wrongly inserted before the shebang.
"""
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
    "mekhane/exagoge/__main__.py"
]

def fix_proof(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping missing file: {filepath}")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    if not lines:
        return

    # Check for corruption: PROOF header before shebang
    if lines[0].startswith("# PROOF:") and len(lines) > 1 and lines[1].startswith("#!"):
        print(f"Fixing corrupted shebang in {filepath}")
        # Swap lines
        lines[0], lines[1] = lines[1], lines[0]
        path.write_text("".join(lines), encoding="utf-8")
        return

    # Check if PROOF header exists
    has_proof = any(line.startswith("# PROOF:") for line in lines[:5])
    if has_proof:
        print(f"Skipping {filepath} (already has header)")
        return

    # Generate header
    header = f"# PROOF: [L2/Mekhane] <- {filepath}\n"
    if "api" in filepath:
        header = f"# PROOF: [L3/API] <- {filepath}\n"
    elif "scripts" in filepath:
        header = f"# PROOF: [L3/Utility] <- {filepath}\n"
    elif "kernel" in filepath:
        header = f"# PROOF: [L0/Kernel] <- {filepath}\n"
    elif "hermeneus" in filepath:
        header = f"# PROOF: [L1/Hermeneus] <- {filepath}\n"

    # Insert header
    if lines[0].startswith("#!"):
        # Insert after shebang
        lines.insert(1, header)
        print(f"Fixed {filepath} (after shebang)")
    else:
        # Insert at top
        lines.insert(0, header)
        print(f"Fixed {filepath} (at top)")

    path.write_text("".join(lines), encoding="utf-8")

if __name__ == "__main__":
    for f in MISSING_FILES:
        fix_proof(f)
