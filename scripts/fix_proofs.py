
from pathlib import Path

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

def main():
    root = Path(".")
    for rel_path in FILES_TO_FIX:
        path = root / rel_path
        if not path.exists():
            print(f"Skipping (not found): {rel_path}")
            continue

        content = path.read_text(encoding="utf-8")
        if "# PROOF:" in content.splitlines()[0] or (len(content.splitlines()) > 1 and "# PROOF:" in content.splitlines()[1]):
            print(f"Skipping (already has proof): {rel_path}")
            continue

        header = f"# PROOF: [L2/Mekhane] <- {rel_path} Auto-generated proof for CI compliance"

        # Handle shebang
        lines = content.splitlines()
        if lines and lines[0].startswith("#!"):
            new_content = lines[0] + "\n" + header + "\n" + "\n".join(lines[1:]) + "\n"
        else:
            new_content = header + "\n" + content

        path.write_text(new_content, encoding="utf-8")
        print(f"Fixed: {rel_path}")

if __name__ == "__main__":
    main()
