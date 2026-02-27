import os
import re

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

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if PROOF header exists
    if re.search(r"#\s*PROOF:\s*\[[^\]]+\]", content):
        print(f"Skipping {filepath} (already has PROOF header)")
        continue

    # Determine Level/Category based on path
    level = "L2"
    category = "Unknown"

    parts = filepath.split("/")
    if len(parts) >= 2:
        if parts[1] == "basanos":
            category = "Basanos"
        elif parts[1] == "periskope":
            category = "Periskope"
        elif parts[1] == "ochema":
            category = "Ochema"
        elif parts[1] == "dendron":
            category = "Dendron"
        elif parts[1] == "ccl":
            category = "CCL"
        elif parts[1] == "mcp":
            category = "MCP"
        elif parts[1] == "api":
            category = "API"
        elif parts[1] == "symploke":
            category = "Symploke"
        elif parts[1] == "anamnesis":
            category = "Anamnesis"
        elif parts[1] == "exagoge":
            category = "Exagoge"
        elif parts[1] == "tape.py":
            category = "Tape"

    header = f"# PROOF: [{level}/{category}] <- {os.path.dirname(filepath)}/\n"

    # Insert after shebang if exists
    if content.startswith("#!"):
        lines = content.split("\n", 1)
        new_content = lines[0] + "\n" + header + (lines[1] if len(lines) > 1 else "")
    else:
        new_content = header + content

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Added PROOF header to {filepath}")
