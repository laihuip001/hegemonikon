
import os
from pathlib import Path

GENERIC_PROOF = "# PROOF: [L2/Mekhane] <- mekhane/ A0->Existence"

SPECIFIC_PROOFS = {
    "mekhane/api/routes/devtools.py": "# PROOF: [L2/Mekhane] <- mekhane/api/routes/ S2->Mekhane->DevTools API",
    "mekhane/api/routes/cortex.py": "# PROOF: [L2/Mekhane] <- mekhane/api/routes/ S2->Mekhane->Cortex API",
    "mekhane/tape.py": "# PROOF: [L2/Mekhane] <- mekhane/tape.py S2->Traceability->Execution Log",
    "mekhane/basanos/l2/deficit_factories.py": "# PROOF: [L2/Basanos] <- mekhane/basanos/l2/ A0->DeficitDetection",
}

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
    "mekhane/exagoge/__main__.py"
]

def fix_files():
    for rel_path in FILES_TO_FIX:
        path = Path(rel_path)
        if not path.exists():
            print(f"Skipping {rel_path} (not found)")
            continue

        content = path.read_text(encoding="utf-8")
        if "# PROOF:" in content.splitlines()[0]:
            print(f"Skipping {rel_path} (PROOF already present)")
            continue

        proof = SPECIFIC_PROOFS.get(rel_path, GENERIC_PROOF)

        # Handle shebang
        if content.startswith("#!"):
            lines = content.splitlines()
            lines.insert(1, proof)
            new_content = "\n".join(lines) + "\n"
        else:
            new_content = f"{proof}\n{content}"

        path.write_text(new_content, encoding="utf-8")
        print(f"Fixed {rel_path}")

if __name__ == "__main__":
    fix_files()
