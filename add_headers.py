import os

files = [
    "mekhane/symploke/intent_wal.py",
    "mekhane/dendron/falsification_checker.py",
    "mekhane/dendron/falsification_matcher.py",
    "mekhane/tape.py",
    "mekhane/ccl/operator_loader.py",
    "mekhane/ccl/ccl_linter.py",
    "mekhane/mcp/mcp_guard.py",
    "mekhane/mcp/mcp_base.py",
    "mekhane/ochema/ls_launcher.py",
    "mekhane/ochema/fake_extension_server.py",
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

for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()

        # Determine specific headers
        if filepath == "mekhane/symploke/intent_wal.py":
            header = "# PROOF: [L2/Mekhane] <- mekhane/symploke/ A2->IntentWAL\n"
        elif filepath == "mekhane/basanos/l2/deficit_factories.py":
            header = "# PROOF: [L2/Infrastructure] <- mekhane/basanos/l2/ A2->Deficit\n"
        elif "mekhane/dendron/" in filepath:
            header = "# PROOF: [L2/Mekhane] <- mekhane/dendron/ A2->Quality\n"
        elif "mekhane/periskope/" in filepath:
            header = "# PROOF: [L2/Mekhane] <- mekhane/periskope/ S2->Search\n"
        elif "mekhane/ccl/" in filepath:
            header = "# PROOF: [L2/Mekhane] <- mekhane/ccl/ S1->Interpreter\n"
        elif "mekhane/ochema/" in filepath:
            header = "# PROOF: [L2/Mekhane] <- mekhane/ochema/ O1->Routing\n"
        elif "mekhane/basanos/" in filepath:
            header = "# PROOF: [L2/Mekhane] <- mekhane/basanos/ A2->Test\n"
        elif "mekhane/mcp/" in filepath:
            header = "# PROOF: [L2/Mekhane] <- mekhane/mcp/ S2->MCP\n"
        elif "mekhane/api/" in filepath:
            header = "# PROOF: [L2/Mekhane] <- mekhane/api/ S2->API\n"
        else:
            header = "# PROOF: [L2/Mekhane] <- mekhane/ S2->Method\n"

        if not content.startswith("# PROOF:"):
            # Handle shebangs
            if content.startswith("#!"):
                lines = content.splitlines()
                lines.insert(1, header.strip())
                new_content = "\n".join(lines) + "\n"
            else:
                new_content = header + content

            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
        else:
            print(f"Skipped {filepath} (already has header)")
    else:
        print(f"File not found: {filepath}")
