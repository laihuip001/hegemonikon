
import os
from pathlib import Path

# List of files identified in the CI failure log
FAILED_FILES = [
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

PROOF_HEADER = "# PROOF: [L2/Impl] <- mekhane/ Automated fix for CI\n"

def main():
    root = Path.cwd()
    count = 0
    for file_path_str in FAILED_FILES:
        path = root / file_path_str
        if not path.exists():
            print(f"Warning: File not found: {path}")
            continue

        try:
            content = path.read_text(encoding="utf-8")
            if content.startswith("# PROOF:"):
                print(f"Skipping {path}: PROOF header already exists")
                continue

            # Preserve shebang if present
            if content.startswith("#!"):
                lines = content.splitlines(keepends=True)
                if len(lines) > 0:
                    lines.insert(1, PROOF_HEADER)
                    new_content = "".join(lines)
                else:
                    new_content = PROOF_HEADER + content
            else:
                new_content = PROOF_HEADER + content

            path.write_text(new_content, encoding="utf-8")
            print(f"Fixed: {path}")
            count += 1
        except Exception as e:
            print(f"Error processing {path}: {e}")

    print(f"Total files fixed: {count}")

if __name__ == "__main__":
    main()
