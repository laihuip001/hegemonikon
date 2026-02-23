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
    "mekhane/basanos/l2/cli.py"
]

header_map = {
    "mekhane/tape.py": "# PROOF: [L2/Mekhane] <- mekhane/tape.py Axiom->Log: Recording tape mechanism for execution traces",
    "mekhane/ccl": "# PROOF: [L1/Hermeneus] <- mekhane/ccl/ Axiom->Language: CCL language constructs",
    "mekhane/symploke": "# PROOF: [L2/Symploke] <- mekhane/symploke/ Axiom->Review: Specialist review integration",
    "mekhane/mcp": "# PROOF: [L3/Integration] <- mekhane/mcp/ Axiom->Protocol: Model Context Protocol implementation",
    "mekhane/ochema": "# PROOF: [L2/Ochema] <- mekhane/ochema/ Axiom->Routing: LLM routing and extension server",
    "mekhane/dendron": "# PROOF: [L2/Dendron] <- mekhane/dendron/ Axiom->Quality: Code quality and falsification checks",
    "mekhane/periskope": "# PROOF: [L3/Periskope] <- mekhane/periskope/ Axiom->Search: Search engine integration and synthesis",
    "mekhane/exagoge": "# PROOF: [L3/Exagoge] <- mekhane/exagoge/ Axiom->Export: Data export functionality",
    "mekhane/anamnesis": "# PROOF: [L3/Anamnesis] <- mekhane/anamnesis/ Axiom->Memory: Knowledge retrieval and embedding",
    "mekhane/api": "# PROOF: [L3/API] <- mekhane/api/ Axiom->Interface: API routes and endpoints",
    "mekhane/basanos": "# PROOF: [L2/Basanos] <- mekhane/basanos/ Axiom->Test: Testing and verification framework"
}

for filepath in files:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue

    proof_line = None
    if filepath in header_map:
        proof_line = header_map[filepath]
    else:
        for prefix, header in header_map.items():
            if filepath.startswith(prefix):
                proof_line = header
                break

    if not proof_line:
        print(f"No header mapping for: {filepath}")
        continue

    with open(filepath, "r") as f:
        content = f.read()

    # Check if PROOF header already exists (though Dendron says it's missing)
    if "# PROOF:" in content:
        print(f"PROOF header might already exist in {filepath}, skipping...")
        continue

    # Insert after shebang if present, otherwise at start
    lines = content.splitlines(keepends=True)
    if lines and lines[0].startswith("#!"):
        lines.insert(1, proof_line + "\n")
    else:
        lines.insert(0, proof_line + "\n")

    with open(filepath, "w") as f:
        f.writelines(lines)
    print(f"Added PROOF header to {filepath}")
