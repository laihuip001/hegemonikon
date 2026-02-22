import os

files_to_fix = [
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

for filepath in files_to_fix:
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        if content.strip().startswith("# PROOF:"):
            print(f"Skipping {filepath}: PROOF header already exists")
            continue

        header = f"# PROOF: [L2/Mekhane] <- {filepath} O1→Zet→Implement\n"

        # Specific overrides based on memory/context
        if filepath == "mekhane/symploke/intent_wal.py":
            header = "# PROOF: [L2/Mekhane] <- mekhane/symploke/intent_wal.py O1→Zet→IntentWAL\n"
        elif "periskope" in filepath:
             header = f"# PROOF: [L2/Periskope] <- {filepath} O3→Zet→Search\n"
        elif "basanos" in filepath:
             header = f"# PROOF: [L2/Basanos] <- {filepath} A2→Dia→Verification\n"
        elif "dendron" in filepath:
             header = f"# PROOF: [L2/Dendron] <- {filepath} A4→Epi→Consistency\n"
        elif "ochema" in filepath:
             header = f"# PROOF: [L2/Ochema] <- {filepath} S2→Mek→Routing\n"
        elif "ccl" in filepath:
             header = f"# PROOF: [L1/Hermeneus] <- {filepath} S1→Her→CCL\n"

        new_content = header + content

        with open(filepath, 'w') as f:
            f.write(new_content)

        print(f"Fixed {filepath}")

    except FileNotFoundError:
        print(f"File not found: {filepath}")
