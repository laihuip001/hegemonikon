#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/fix_proof_headers.py A0→Automation→Maintenance
# PURPOSE: Automate adding missing PROOF headers to files identified by dendron check

import os
import sys
from pathlib import Path

# List of files identified as missing PROOF headers
MISSING_FILES = [
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

def add_proof_header(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath}: not found")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Check if PROOF header already exists (basic check)
    for i, line in enumerate(lines[:5]):
        if line.startswith("# PROOF:"):
            print(f"Skipping {filepath}: PROOF header already exists")
            return

    # Construct PROOF header
    # Format: # PROOF: [L2/Mekhane] <- {parent_dir}/ A0->Implementation->{filename}
    parent_dir = path.parent
    filename = path.name
    proof_line = f"# PROOF: [L2/Mekhane] <- {parent_dir}/ A0->Implementation->{filename}"

    # Determine insertion point
    # Insert after shebang if present, otherwise at top
    insert_idx = 0
    if lines and lines[0].startswith("#!"):
        insert_idx = 1
    elif lines and lines[0].startswith("# -*-"):
        insert_idx = 1

    lines.insert(insert_idx, proof_line)

    # Check for PURPOSE header
    has_purpose = False
    for line in lines[:10]:
        if line.startswith("# PURPOSE:"):
            has_purpose = True
            break

    if not has_purpose:
        # Add default PURPOSE if missing
        purpose_line = f"# PURPOSE: Implementation of {path.stem}"
        lines.insert(insert_idx + 1, purpose_line)

    new_content = "\n".join(lines) + "\n"
    path.write_text(new_content, encoding="utf-8")
    print(f"Fixed {filepath}")

def main():
    print(f"Fixing PROOF headers for {len(MISSING_FILES)} files...")
    for filepath in MISSING_FILES:
        try:
            add_proof_header(filepath)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    main()
