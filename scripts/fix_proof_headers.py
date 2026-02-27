#!/usr/bin/env python3
"""
Fix missing PROOF headers in bulk.
"""
from pathlib import Path

FILES = [
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
    "mekhane/ochema/proto/extension_server_pb2_grpc.py",
]

def get_proof_header(path: str) -> str:
    """Generate appropriate PROOF header based on path."""
    p = Path(path)
    parent = str(p.parent) + "/"
    if "dendron" in path:
        return f"# PROOF: [L2/Infra] <- {parent}"
    if "symploke" in path:
        return f"# PROOF: [L2/Symploke] <- {parent}"
    if "ccl" in path:
        return f"# PROOF: [L1/CCL] <- {parent}"
    if "api" in path:
        return f"# PROOF: [L2/API] <- {parent}"
    if "basanos" in path:
        return f"# PROOF: [L2/Test] <- {parent}"
    if "ochema" in path:
        return f"# PROOF: [L2/Ochema] <- {parent}"
    return f"# PROOF: [L2/Mekhane] <- {parent}"

def main():
    for fpath in FILES:
        p = Path(fpath)
        if not p.exists():
            print(f"Skipping non-existent file: {fpath}")
            continue

        content = p.read_text(encoding="utf-8")
        if "# PROOF:" in content:
            print(f"Skipping existing PROOF: {fpath}")
            continue

        header = get_proof_header(fpath)

        # Check if first line is shebang
        lines = content.splitlines()
        if lines and lines[0].startswith("#!"):
            lines.insert(1, header)
        else:
            lines.insert(0, header)

        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Added PROOF to: {fpath}")

if __name__ == "__main__":
    main()
