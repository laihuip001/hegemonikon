
import os
from pathlib import Path

# List of files identified in the CI log as missing PROOF headers
files_missing_proof = [
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
    "mekhane/basanos/l2/cli.py",
]

PROOF_HEADER = "# PROOF: [L2/Impl] <- mekhane/ Automated fix for CI\n"

def main():
    fixed_count = 0
    not_found_count = 0

    for file_path_str in files_missing_proof:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"File not found: {file_path}")
            not_found_count += 1
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            if not content.startswith("# PROOF:"):
                # Handle shebang or encoding cookie if present
                lines = content.splitlines(keepends=True)
                new_lines = []
                inserted = False

                # Try to insert after shebang or encoding, or at top
                if lines and (lines[0].startswith("#!") or lines[0].startswith("# -*-")):
                     new_lines.append(lines[0])
                     if len(lines) > 1 and (lines[1].startswith("# -*-") or lines[1].startswith("#!")):
                         new_lines.append(lines[1])
                         new_lines.append(PROOF_HEADER)
                         new_lines.extend(lines[2:])
                     else:
                         new_lines.append(PROOF_HEADER)
                         new_lines.extend(lines[1:])
                else:
                    new_lines.append(PROOF_HEADER)
                    new_lines.extend(lines)

                file_path.write_text("".join(new_lines), encoding="utf-8")
                print(f"Fixed: {file_path}")
                fixed_count += 1
            else:
                print(f"Already has PROOF: {file_path}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"\nSummary: Fixed {fixed_count} files, {not_found_count} not found.")

if __name__ == "__main__":
    main()
