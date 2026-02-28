import os

files = [
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

for filepath in files:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r') as f:
        content = f.read()

    # Specific ones from memory
    if filepath == "mekhane/symploke/intent_wal.py":
        proof = "# PROOF: [L2/Mekhane] <- mekhane/symploke/ S2->Mekhane->Intent WAL"
    elif filepath == "mekhane/basanos/l2/deficit_factories.py":
        proof = "# PROOF: [L2/Basanos] <- mekhane/basanos/l2/ A0->DeficitDetection"
    else:
        proof = "# PROOF: [L2/Mekhane] <- mekhane/ A0->Existence"

    if content.startswith("#!/usr/bin/env python3\n"):
        new_content = "#!/usr/bin/env python3\n" + proof + "\n" + content[len("#!/usr/bin/env python3\n"):]
    else:
        new_content = proof + "\n" + content

    with open(filepath, 'w') as f:
        f.write(new_content)
