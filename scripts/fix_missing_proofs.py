#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/ A0→Tool→Fix proofs
# PURPOSE: Missing PROOF headers を自動生成するスクリプト (ad-hoc)
"""
scripts/fix_missing_proofs.py

Usage:
    python scripts/fix_missing_proofs.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# List of files missing PROOF headers (from CI output)
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

def generate_header(file_path: Path) -> str:
    """Generate a valid PROOF header for the file."""
    # Determine Level based on path
    if "kernel" in str(file_path):
        level = "L0"
        cat = "Theory"
    elif "hermeneus" in str(file_path):
        level = "L1"
        cat = "Parser"
    elif "mekhane" in str(file_path):
        level = "L2"
        cat = "Infra"
    else:
        level = "L3"
        cat = "Integration"

    # Determine Parent Path
    # e.g., mekhane/symploke/intent_wal.py -> mekhane/symploke/
    parent_path = str(file_path.parent.relative_to(PROJECT_ROOT)) + "/"
    if parent_path == "./":
        parent_path = str(file_path.relative_to(PROJECT_ROOT))

    # Trace (Generic)
    trace = "A0->AutoFix"

    return f"# PROOF: [{level}/{cat}] <- {parent_path} {trace}\n"

def fix_file(rel_path: str):
    path = PROJECT_ROOT / rel_path
    if not path.exists():
        print(f"Skipping {rel_path}: Not found")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Skip if already has PROOF
    if any(l.startswith("# PROOF:") for l in lines):
        print(f"Skipping {rel_path}: Already has PROOF")
        return

    # Check for shebang
    has_shebang = len(lines) > 0 and lines[0].startswith("#!")

    header = generate_header(path)

    if has_shebang:
        # Insert after shebang
        new_content = [lines[0], header] + lines[1:]
    else:
        # Insert at top
        new_content = [header] + lines

    path.write_text("\n".join(new_content) + "\n", encoding="utf-8")
    print(f"Fixed {rel_path}")

def main():
    print(f"Fixing {len(MISSING_FILES)} files...")
    for f in MISSING_FILES:
        fix_file(f)
    print("Done.")

if __name__ == "__main__":
    main()
