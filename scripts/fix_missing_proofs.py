#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/ A0->Existence
"""
Fix Missing PROOF Headers Script

This script iterates through the list of files identified as missing PROOF headers
by the Dendron CI check and prepends a default PROOF header.
"""

from pathlib import Path
import sys

# List of files identified in the CI failure log
MISSING_PROOF_FILES = [
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

def fix_proof_headers():
    project_root = Path(__file__).resolve().parent.parent

    for relative_path in MISSING_PROOF_FILES:
        file_path = project_root / relative_path
        if not file_path.exists():
            print(f"Skipping (not found): {relative_path}")
            continue

        try:
            content = file_path.read_text(encoding="utf-8")

            # Check if PROOF header already exists to avoid duplication
            if content.startswith("# PROOF:") or "\n# PROOF:" in content[:100]:
                print(f"Skipping (already has PROOF): {relative_path}")
                continue

            # Construct default PROOF header
            # Using the parent directory name as the source context
            parent_dir = file_path.parent.name
            proof_header = f"# PROOF: [L2/Mekhane] <- {parent_dir}/ A0->Existence\n"

            # Preserve shebang if present
            if content.startswith("#!"):
                lines = content.splitlines(keepends=True)
                new_content = lines[0] + proof_header + "".join(lines[1:])
            else:
                new_content = proof_header + content

            file_path.write_text(new_content, encoding="utf-8")
            print(f"Fixed: {relative_path}")

        except Exception as e:
            print(f"Error fixing {relative_path}: {e}")

if __name__ == "__main__":
    fix_proof_headers()
