# PROOF: [L2/スクリプト] <- scripts/fix_missing_proofs_ci.py
# PURPOSE: 欠落している PROOF ヘッダーを CI ログから抽出して自動注入する
import sys
import os
import re
from pathlib import Path

# Missing files extracted from the CI log provided in the issue description
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
    "mekhane/exagoge/__main__.py"
]

def determine_proof_tag(filepath):
    """ファイルパスに基づいて適切なPROOFタグを決定する"""
    if "api/routes" in filepath:
        return f"# PROOF: [L2/API] <- {filepath}"
    elif "mcp" in filepath:
        return f"# PROOF: [L2/MCP] <- {filepath}"
    elif "ccl" in filepath:
        return f"# PROOF: [L2/CCL] <- {filepath}"
    elif "dendron" in filepath:
        return f"# PROOF: [L2/Dendron] <- {filepath}"
    elif "symploke" in filepath:
        return f"# PROOF: [L2/Symploke] <- {filepath}"
    elif "periskope" in filepath:
        return f"# PROOF: [L2/Periskope] <- {filepath}"
    elif "basanos" in filepath:
        return f"# PROOF: [L2/Basanos] <- {filepath}"
    elif "ochema" in filepath:
        return f"# PROOF: [L2/Ochema] <- {filepath}"
    elif "anamnesis" in filepath:
        return f"# PROOF: [L2/Anamnesis] <- {filepath}"
    elif "exagoge" in filepath:
        return f"# PROOF: [L2/Exagoge] <- {filepath}"
    elif "tests" in filepath:
        return f"# PROOF: [L3/Test] <- {filepath}"
    else:
        return f"# PROOF: [L2/Impl] <- {filepath}"

def fix_file(filepath):
    """ファイルにPROOFヘッダーを追加する"""
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} (not found)")
        return False

    try:
        content = path.read_text(encoding="utf-8")

        # Check if already has PROOF
        if re.search(r"^#\s*PROOF:", content, re.MULTILINE):
            print(f"Skipping {filepath} (already has PROOF)")
            return False

        proof_header = determine_proof_tag(filepath)

        # Shebang handling
        if content.startswith("#!"):
            lines = content.splitlines()
            if len(lines) > 0:
                lines.insert(1, proof_header)
                new_content = "\n".join(lines)
                if content.endswith("\n"):
                    new_content += "\n"
                path.write_text(new_content, encoding="utf-8")
        else:
            path.write_text(f"{proof_header}\n{content}", encoding="utf-8")

        print(f"Fixed {filepath}")
        return True

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    root_dir = Path.cwd()
    success_count = 0

    print(f"Scanning from {root_dir}")

    for relative_path in MISSING_FILES:
        # Check if file exists relative to root
        full_path = root_dir / relative_path
        if fix_file(str(full_path)):
            success_count += 1

    print(f"\nTotal fixed: {success_count}/{len(MISSING_FILES)}")

if __name__ == "__main__":
    main()
