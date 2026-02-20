import os
import sys

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

proof_map = {
    "mekhane/tape.py": "# PROOF: [L2/Mekhanē] <- mekhane/ A0→O1(Tape)→Record execution trace",
    "mekhane/ccl/operator_loader.py": "# PROOF: [S1/Hermēneia] <- mekhane/ccl/ S1→Load operators dynamically",
    "mekhane/ccl/ccl_linter.py": "# PROOF: [S1/Hermēneia] <- mekhane/ccl/ S1→Lint CCL syntax",
    "mekhane/symploke/intent_wal.py": "# PROOF: [P4/Symplokē] <- mekhane/symploke/ P4→Intent Write-Ahead Log for continuity",
    "mekhane/mcp/mcp_guard.py": "# PROOF: [L2/Infrastructure] <- mekhane/mcp/ A0→Safety guard for MCP",
    "mekhane/mcp/mcp_base.py": "# PROOF: [L2/Infrastructure] <- mekhane/mcp/ A0→Base MCP implementation",
    "mekhane/ochema/ls_launcher.py": "# PROOF: [S2/Mekhanē] <- mekhane/ochema/ S2→Launch Language Server",
    "mekhane/ochema/fake_extension_server.py": "# PROOF: [S2/Mekhanē] <- mekhane/ochema/ S2→Fake server for testing",
    "mekhane/dendron/falsification_checker.py": "# PROOF: [A2/Krisis] <- mekhane/dendron/ A2→Check for falsification",
    "mekhane/dendron/falsification_matcher.py": "# PROOF: [A2/Krisis] <- mekhane/dendron/ A2→Match falsification patterns",
    "mekhane/periskope/engine.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/ K2→Search engine core",
    "mekhane/periskope/synthesizer.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/ K2→Synthesize search results",
    "mekhane/periskope/models.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/ K2→Data models for search",
    "mekhane/periskope/query_expander.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/ K2→Expand search queries",
    "mekhane/periskope/__init__.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/ K2→Periskopē package",
    "mekhane/periskope/citation_agent.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/ K2→Generate citations",
    "mekhane/periskope/page_fetcher.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/ K2→Fetch web pages",
    "mekhane/periskope/cli.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/ K2→CLI for Periskopē",
    "mekhane/exagoge/__main__.py": "# PROOF: [L2/Infrastructure] <- mekhane/exagoge/ A0→Main entry point for Exagōgē",
    "mekhane/anamnesis/vertex_embedder.py": "# PROOF: [K3/Anamnēsis] <- mekhane/anamnesis/ K3→Embed vertices for memory",
    "mekhane/ochema/proto/extension_server_pb2_grpc.py": "# PROOF: [S2/Mekhanē] <- mekhane/ochema/ S2→GRPC generated code",
    "mekhane/ochema/proto/__init__.py": "# PROOF: [S2/Mekhanē] <- mekhane/ochema/ S2→Proto package",
    "mekhane/ochema/proto/extension_server_pb2.py": "# PROOF: [S2/Mekhanē] <- mekhane/ochema/ S2→Proto generated code",
    "mekhane/periskope/searchers/__init__.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/searchers/ K2→Searchers package",
    "mekhane/periskope/searchers/internal_searcher.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/searchers/ K2→Internal KB searcher",
    "mekhane/periskope/searchers/tavily_searcher.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/searchers/ K2→Tavily searcher",
    "mekhane/periskope/searchers/semantic_scholar_searcher.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/searchers/ K2→Semantic Scholar searcher",
    "mekhane/periskope/searchers/playwright_searcher.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/searchers/ K2→Playwright searcher",
    "mekhane/periskope/searchers/brave_searcher.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/searchers/ K2→Brave searcher",
    "mekhane/periskope/searchers/searxng.py": "# PROOF: [K2/Sophia] <- mekhane/periskope/searchers/ K2→SearXNG searcher",
    "mekhane/api/routes/cortex.py": "# PROOF: [S2/Mekhanē] <- mekhane/api/routes/ S2→Cortex API route",
    "mekhane/api/routes/devtools.py": "# PROOF: [S2/Mekhanē] <- mekhane/api/routes/ S2→Devtools API route",
    "mekhane/basanos/l2/g_semantic.py": "# PROOF: [A2/Krisis] <- mekhane/basanos/l2/ A2→Semantic analysis",
    "mekhane/basanos/l2/resolver.py": "# PROOF: [A2/Krisis] <- mekhane/basanos/l2/ A2→Resolve test results",
    "mekhane/basanos/l2/models.py": "# PROOF: [A2/Krisis] <- mekhane/basanos/l2/ A2→L2 Test models",
    "mekhane/basanos/l2/g_struct.py": "# PROOF: [A2/Krisis] <- mekhane/basanos/l2/ A2→Structural analysis",
    "mekhane/basanos/l2/__init__.py": "# PROOF: [A2/Krisis] <- mekhane/basanos/l2/ A2→L2 Basanos package",
    "mekhane/basanos/l2/deficit_factories.py": "# PROOF: [A2/Krisis] <- mekhane/basanos/l2/ A2→Generate deficits",
    "mekhane/basanos/l2/hom.py": "# PROOF: [A2/Krisis] <- mekhane/basanos/l2/ A2→Higher Order Monitoring",
    "mekhane/basanos/l2/history.py": "# PROOF: [A2/Krisis] <- mekhane/basanos/l2/ A2→Test history",
    "mekhane/basanos/l2/cli.py": "# PROOF: [A2/Krisis] <- mekhane/basanos/l2/ A2→L2 CLI"
}

for filepath in files:
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}: not found")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "# PROOF:" in content:
        print(f"Skipping {filepath}: already has PROOF")
        continue

    proof_line = proof_map.get(filepath, f"# PROOF: [L2/Mekhanē] <- {os.path.dirname(filepath)}/ A0→Auto-generated PROOF")

    # Handle shebang
    if content.startswith("#!"):
        lines = content.splitlines()
        lines.insert(1, proof_line)
        new_content = "\n".join(lines)
    else:
        new_content = f"{proof_line}\n{content}"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Added PROOF to {filepath}")
