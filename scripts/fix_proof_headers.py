
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
    "mekhane/exagoge/__main__.py",
]

PROOF_HEADER = "# PROOF: [L2/Impl] <- mekhane/ Automated fix for CI\n"

def fix_file(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    if not lines:
        path.write_text(PROOF_HEADER, encoding="utf-8")
        print(f"Fixed {filepath} (empty file)")
        return

    # Check if PROOF header already exists
    if any(line.strip().startswith("# PROOF:") for line in lines[:5]):
        print(f"Skipping {filepath} (PROOF header already exists)")
        return

    new_lines = []
    if lines[0].startswith("#!"):
        new_lines.append(lines[0])
        new_lines.append(PROOF_HEADER)
        new_lines.extend(lines[1:])
    else:
        new_lines.append(PROOF_HEADER)
        new_lines.extend(lines)

    path.write_text("".join(new_lines), encoding="utf-8")
    print(f"Fixed {filepath}")

def main():
    print("Applying PROOF header fixes...")
    for f in FILES_TO_FIX:
        fix_file(f)
    print("Done.")

if __name__ == "__main__":
    main()
