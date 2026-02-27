#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- scripts/ A0->Auto->CI
"""
CI Missing PROOF Header Fixer

CI が検出した PROOF ヘッダ欠落ファイルに自動でヘッダを注入する。
"""
import sys
from pathlib import Path

# Files reported by CI
MISSING_FILES = [
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

def fix_proofs():
    root = Path(__file__).parent.parent
    fixed_count = 0

    for rel_path in MISSING_FILES:
        path = root / rel_path
        if not path.exists():
            print(f"Skipping {rel_path} (not found)")
            continue

        content = path.read_text(encoding="utf-8")
        if "# PROOF:" in content.splitlines()[0]:
            print(f"Skipping {rel_path} (already has PROOF)")
            continue

        parent = path.parent.name
        header = f"# PROOF: [L2/Mekhane] <- mekhane/{parent}/ A0->Auto->AddedByCI\n"

        # Insert at top, preserving shebang if present
        lines = content.splitlines(keepends=True)
        if lines and lines[0].startswith("#!"):
            lines.insert(1, header)
        else:
            lines.insert(0, header)

        path.write_text("".join(lines), encoding="utf-8")
        print(f"Fixed {rel_path}")
        fixed_count += 1

    print(f"Fixed {fixed_count} files.")

if __name__ == "__main__":
    fix_proofs()
