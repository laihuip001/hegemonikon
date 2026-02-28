import re
from pathlib import Path

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

proof_header = "# PROOF: [L2/Infrastructure] <- mekhane/"

for fpath in files_to_fix:
    p = Path(fpath)
    if not p.exists():
        continue

    content = p.read_text()

    if "PROOF:" in content:
        continue

    # Find the first line that is not a shebang or empty
    lines = content.splitlines(keepends=True)
    insert_idx = 0
    if lines and lines[0].startswith("#!"):
        insert_idx = 1

    # Insert the proof header
    lines.insert(insert_idx, proof_header + "\n")
    p.write_text("".join(lines))
    print(f"Fixed {fpath}")
