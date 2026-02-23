import os
from pathlib import Path

FILES_TO_FIX = [
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

PROOF_HEADER = "# PROOF: [L2/Mekhane] <- mekhane/ A0->Implementation"
PURPOSE_HEADER = "# PURPOSE: Implementation module"

def fix_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping missing file: {filepath}")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    has_proof = False
    has_purpose = False

    # Check existing headers
    for i in range(min(5, len(lines))):
        if lines[i].startswith("# PROOF:"):
            has_proof = True
        if lines[i].startswith("# PURPOSE:"):
            has_purpose = True

    if has_proof and has_purpose:
        print(f"Skipping {filepath} (already has headers)")
        return

    new_lines = []

    # Handle shebang
    if lines and lines[0].startswith("#!"):
        new_lines.append(lines[0])
        lines = lines[1:]

    if not has_proof:
        new_lines.append(PROOF_HEADER)

    if not has_purpose:
        # Avoid double PURPOSE if logic detected it but I missed it (unlikely with simple check)
        # But for safety, check if the first line is PURPOSE
        if not (lines and lines[0].startswith("# PURPOSE:")):
             new_lines.append(PURPOSE_HEADER)

    new_lines.extend(lines)

    # Write back
    # Ensure ending newline
    final_content = "\n".join(new_lines) + "\n"
    path.write_text(final_content, encoding="utf-8")
    print(f"Fixed {filepath}")

if __name__ == "__main__":
    for f in FILES_TO_FIX:
        fix_file(f)
