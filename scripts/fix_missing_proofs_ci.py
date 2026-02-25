# PURPOSE: Inject missing PROOF headers for CI remediation
import sys
from pathlib import Path

# Files identified from CI logs
MISSING_FILES = [
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
    "mekhane/exagoge/__main__.py",
]

def main():
    root = Path.cwd()
    count = 0
    for rel_path in MISSING_FILES:
        path = root / rel_path
        if not path.exists():
            print(f"Skipping missing file: {rel_path}")
            continue

        content = path.read_text(encoding="utf-8")
        if "# PROOF:" in content:
            print(f"Skipping (already has proof): {rel_path}")
            continue

        parent_dir = path.parent.name
        header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent_dir}/ A0->Auto->AddedByCI"

        lines = content.splitlines()
        new_lines = []

        # Preserve shebang
        if lines and lines[0].startswith("#!"):
            new_lines.append(lines[0])
            new_lines.append(header)
            new_lines.extend(lines[1:])
        else:
            new_lines.append(header)
            new_lines.extend(lines)

        # Ensure newline at end of file
        new_content = "\n".join(new_lines) + "\n"
        path.write_text(new_content, encoding="utf-8")
        print(f"Injected header: {rel_path}")
        count += 1

    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
