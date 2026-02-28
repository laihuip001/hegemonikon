import os
import re

proofs = {
    "mekhane/tape.py": "# PROOF: [L1/Core] <- mekhane/\n",
    "mekhane/ccl/operator_loader.py": "# PROOF: [L2/CCL] <- mekhane/ccl/\n",
    "mekhane/ccl/ccl_linter.py": "# PROOF: [L2/CCL] <- mekhane/ccl/\n",
    "mekhane/symploke/intent_wal.py": "# PROOF: [L2/インフラ] <- mekhane/symploke/\n",
    "mekhane/mcp/mcp_guard.py": "# PROOF: [L2/Security] <- mekhane/mcp/\n",
    "mekhane/mcp/mcp_base.py": "# PROOF: [L2/Core] <- mekhane/mcp/\n",
    "mekhane/ochema/ls_launcher.py": "# PROOF: [L2/LSP] <- mekhane/ochema/\n",
    "mekhane/ochema/fake_extension_server.py": "# PROOF: [L2/Testing] <- mekhane/ochema/\n",
    "mekhane/dendron/falsification_checker.py": "# PROOF: [L2/Verification] <- mekhane/dendron/\n",
    "mekhane/dendron/falsification_matcher.py": "# PROOF: [L2/Verification] <- mekhane/dendron/\n",
    "mekhane/periskope/engine.py": "# PROOF: [L2/Search] <- mekhane/periskope/\n",
    "mekhane/periskope/synthesizer.py": "# PROOF: [L2/Synthesis] <- mekhane/periskope/\n",
    "mekhane/periskope/models.py": "# PROOF: [L2/Models] <- mekhane/periskope/\n",
    "mekhane/periskope/query_expander.py": "# PROOF: [L2/Search] <- mekhane/periskope/\n",
    "mekhane/periskope/__init__.py": "# PROOF: [L2/Module] <- mekhane/periskope/\n",
    "mekhane/periskope/citation_agent.py": "# PROOF: [L2/Agent] <- mekhane/periskope/\n",
    "mekhane/periskope/page_fetcher.py": "# PROOF: [L2/Network] <- mekhane/periskope/\n",
    "mekhane/periskope/cli.py": "# PROOF: [L2/CLI] <- mekhane/periskope/\n",
    "mekhane/exagoge/__main__.py": "# PROOF: [L2/CLI] <- mekhane/exagoge/\n",
    "mekhane/anamnesis/vertex_embedder.py": "# PROOF: [L2/Embedding] <- mekhane/anamnesis/\n",
    "mekhane/ochema/proto/extension_server_pb2_grpc.py": "# PROOF: [L2/Proto] <- mekhane/ochema/\n",
    "mekhane/ochema/proto/__init__.py": "# PROOF: [L2/Module] <- mekhane/ochema/\n",
    "mekhane/ochema/proto/extension_server_pb2.py": "# PROOF: [L2/Proto] <- mekhane/ochema/\n",
    "mekhane/periskope/searchers/__init__.py": "# PROOF: [L2/Module] <- mekhane/periskope/searchers/\n",
    "mekhane/periskope/searchers/internal_searcher.py": "# PROOF: [L2/Search] <- mekhane/periskope/searchers/\n",
    "mekhane/periskope/searchers/tavily_searcher.py": "# PROOF: [L2/Search] <- mekhane/periskope/searchers/\n",
    "mekhane/periskope/searchers/semantic_scholar_searcher.py": "# PROOF: [L2/Search] <- mekhane/periskope/searchers/\n",
    "mekhane/periskope/searchers/playwright_searcher.py": "# PROOF: [L2/Search] <- mekhane/periskope/searchers/\n",
    "mekhane/periskope/searchers/brave_searcher.py": "# PROOF: [L2/Search] <- mekhane/periskope/searchers/\n",
    "mekhane/periskope/searchers/searxng.py": "# PROOF: [L2/Search] <- mekhane/periskope/searchers/\n",
    "mekhane/api/routes/cortex.py": "# PROOF: [L2/API] <- mekhane/api/\n",
    "mekhane/api/routes/devtools.py": "# PROOF: [L2/API] <- mekhane/api/\n",
    "mekhane/basanos/l2/g_semantic.py": "# PROOF: [L2/Evaluation] <- mekhane/basanos/\n",
    "mekhane/basanos/l2/resolver.py": "# PROOF: [L2/Resolution] <- mekhane/basanos/\n",
    "mekhane/basanos/l2/models.py": "# PROOF: [L2/Models] <- mekhane/basanos/\n",
    "mekhane/basanos/l2/g_struct.py": "# PROOF: [L2/Evaluation] <- mekhane/basanos/\n",
    "mekhane/basanos/l2/__init__.py": "# PROOF: [L2/Module] <- mekhane/basanos/\n",
    "mekhane/basanos/l2/deficit_factories.py": "# PROOF: [L2/Factory] <- mekhane/basanos/\n",
    "mekhane/basanos/l2/hom.py": "# PROOF: [L2/Evaluation] <- mekhane/basanos/\n",
    "mekhane/basanos/l2/history.py": "# PROOF: [L2/Data] <- mekhane/basanos/\n",
    "mekhane/basanos/l2/cli.py": "# PROOF: [L2/CLI] <- mekhane/basanos/\n"
}

for path, proof_line in proofs.items():
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if already has PROOF
        if not re.search(r"#\s*PROOF:", content[:500]):
            with open(path, 'w', encoding='utf-8') as f:
                # Insert at line 1, unless line 1 is shebang
                if content.startswith("#!"):
                    parts = content.split('\n', 1)
                    f.write(parts[0] + '\n' + proof_line + parts[1])
                else:
                    f.write(proof_line + content)
            print(f"Added PROOF to {path}")
