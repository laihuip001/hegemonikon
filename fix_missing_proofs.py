import os
import sys

missing_files = [
    "mekhane/tape.py",
    "mekhane/anamnesis/vertex_embedder.py",
    "mekhane/mcp/mcp_guard.py",
    "mekhane/mcp/mcp_base.py",
    "mekhane/dendron/falsification_checker.py",
    "mekhane/dendron/falsification_matcher.py",
    "mekhane/periskope/citation_agent.py",
    "mekhane/periskope/models.py",
    "mekhane/periskope/__init__.py",
    "mekhane/periskope/cli.py",
    "mekhane/periskope/engine.py",
    "mekhane/periskope/query_expander.py",
    "mekhane/periskope/synthesizer.py",
    "mekhane/periskope/page_fetcher.py",
    "mekhane/periskope/searchers/searxng.py",
    "mekhane/periskope/searchers/brave_searcher.py",
    "mekhane/periskope/searchers/tavily_searcher.py",
    "mekhane/periskope/searchers/__init__.py",
    "mekhane/periskope/searchers/internal_searcher.py",
    "mekhane/periskope/searchers/playwright_searcher.py",
    "mekhane/periskope/searchers/semantic_scholar_searcher.py",
    "mekhane/ccl/operator_loader.py",
    "mekhane/ccl/ccl_linter.py",
    "mekhane/exagoge/__main__.py",
    "mekhane/symploke/intent_wal.py",
    "mekhane/api/routes/cortex.py",
    "mekhane/api/routes/devtools.py",
    "mekhane/basanos/l2/hom.py",
    "mekhane/basanos/l2/deficit_factories.py",
    "mekhane/basanos/l2/models.py",
    "mekhane/basanos/l2/history.py",
    "mekhane/basanos/l2/resolver.py",
    "mekhane/basanos/l2/__init__.py",
    "mekhane/basanos/l2/cli.py",
    "mekhane/basanos/l2/g_semantic.py",
    "mekhane/basanos/l2/g_struct.py",
    "mekhane/ochema/ls_launcher.py",
    "mekhane/ochema/fake_extension_server.py",
    "mekhane/ochema/proto/__init__.py",
    "mekhane/ochema/proto/extension_server_pb2.py",
    "mekhane/ochema/proto/extension_server_pb2_grpc.py"
]

for file in missing_files:
    if os.path.exists(file):
        with open(file, 'r') as f:
            content = f.read()

        # Only add if not already present
        if "# PROOF:" not in content:
            # We'll prepend # PROOF: [L2/Missing] <- <dir>\n
            dir_name = os.path.dirname(file) + "/"

            new_content = f"# PROOF: [L2/Missing] <- {dir_name}\n"

            if content.startswith("#!/usr/bin/env python3"):
                new_content = "#!/usr/bin/env python3\n" + new_content + content[len("#!/usr/bin/env python3\n"):]
            else:
                new_content = new_content + content

            with open(file, 'w') as f:
                f.write(new_content)
            print(f"Fixed {file}")
