#!/usr/bin/env python3
# PROOF: [L2/ツール] <- scripts/
# PURPOSE: PROOF.md が欠落しているソースディレクトリに自動生成する。コンテキストを読んで適切な説明を付与。
"""
Dir PROOF.md Generator — ディレクトリ存在証明の一括生成

Usage:
    python scripts/dir_proof_generator.py mekhane/      # dry-run (preview)
    python scripts/dir_proof_generator.py mekhane/ --write  # 実際に書き込み
"""

import argparse
import os
import sys
from pathlib import Path

# Directories to SKIP (not source code)
SKIP_PATTERNS = {
    "__pycache__",
    ".pytest_cache",
    ".cache",
    "node_modules",
    "v",       # pytest cache internal
    "cache",   # pytest cache internal
}

# Path fragments to skip (data, models, binary artifacts)
SKIP_PATH_FRAGMENTS = {
    "/lance/",
    "/lancedb/",
    "/_transactions/",
    "/_versions/",
    "/data/",
    "/models/",
    "/Raw/",
    "/raw/",
    "/_index/",
    "/knowledge_base/",
    "/knowledge/",
    "/binaryData/",
    "/nodes/",
    "/swarm_results/",
    "/.cache/",
    "/logs/",
}


# Context descriptions based on directory name or parent
DIR_DESCRIPTIONS = {
    "tests": "テスト群 — このサブパッケージのユニットテストを集約",
    "agents": "エージェント定義 — CCL/LLM エージェントの実装",
    "prompts": "プロンプト集 — LLM 向けプロンプトテンプレート",
    "docs": "ドキュメント — 仕様・設計・ガイド",
    "mixins": "ミックスイン — 共通機能を提供する再利用可能モジュール",
    "references": "参照資料 — 外部サンプル・テンプレート集",
    "examples": "サンプルコード — 使い方の実例",
    "staging": "ステージング — 実験的・一時的ファイル置場",
    "protocols": "プロトコル定義 — 開発手順書・規約集",
    "flow": "フロー制御 — ワークフロー実行エンジン",
    "adapters": "アダプター — 外部サービス接続層",
    "search": "検索 — インデックス検索・クエリ実行",
    "indices": "インデックス — ベクトル/テキスト検索用インデックス管理",
    "links": "リンク管理 — エンティティ間の関係を管理",
    "collectors": "コレクター — 外部データソースからの収集",
    "deploy": "デプロイ — 本番環境への配備設定",
    "cloudflare": "Cloudflare — edge deployment 設定",
    "cloudflare-workers": "Cloudflare Workers — edge function 実装",
    "systemd": "systemd — Linux サービス定義",
    "src": "ソース — メイン実装コード",
    "templates": "テンプレート — 生成用テンプレート集",
    "imported": "インポート済み — 外部から取り込んだテンプレート",
    "n8n": "n8n — ワークフロー自動化エンジン連携",
    "library": "ライブラリ — 再利用可能なプロンプトモジュール集",
    "execute": "実行系 — アクション実行プロンプト",
    "modules": "モジュール — 機能単位のプロンプト群",
    "perceive": "知覚系 — 入力認識・解析プロンプト",
    "think": "思考系 — 推論・分析プロンプト",
    "verify": "検証系 — 出力検証・品質チェックプロンプト",
    "experiments": "実験 — 探索的な試行コード",
    "_limbo": "リンボ — 一時退避・未分類コード",
    "factory": "ファクトリー — オブジェクト生成パターン",
    "helpers": "ヘルパー — ユーティリティ関数群",
    "test_vault": "テスト用Vault — テストデータのモック環境",
}

# Parent-based descriptions (when dir name alone isn't enough)
PARENT_DESCRIPTIONS = {
    "anamnesis": "記憶・知識管理サブシステム",
    "ccl": "CCL (Cognitive Control Language) サブシステム",
    "dendron": "存在証明 (Dendron) チェッカー",
    "ergasterion": "工房 — ツール・プロンプト管理",
    "exagoge": "出力・エクスポート管理",
    "fep": "FEP (Free Energy Principle) エンジン",
    "gnosis": "知識検索・ベクトルDB",
    "peira": "論文・文献管理",
    "pks": "知識構造 (PKS) エンジン",
    "poiema": "創造的生成・フロー制御",
    "symploke": "統合検索・織り合わせ",
    "synteleia": "統合・完成系",
    "mcp": "MCP サーバー群",
    "deploy": "デプロイ設定",
    "tekhne": "技法管理 — プロンプトエンジニアリング",
    "prompt-lang": "Prompt Language — DSL パーサー/実行系",
    "prompt_literacy": "プロンプトリテラシー — 教育・学習支援",
    "synedrion": "評議会 — 多角的批評エンジン",
    "digestor": "消化器 — 外部コンテンツ取込み",
}


def _should_skip(dir_path: Path, root: Path) -> bool:
    """Skip non-source directories."""
    if dir_path.name in SKIP_PATTERNS:
        return True
    rel = str(dir_path.relative_to(root.parent if root.parent != dir_path else root))
    for frag in SKIP_PATH_FRAGMENTS:
        if frag in f"/{rel}/":
            return True
    return False


def _generate_proof_content(dir_path: Path) -> str:
    """Generate PROOF.md content for a directory."""
    name = dir_path.name
    parent_name = dir_path.parent.name

    # Get description
    desc = DIR_DESCRIPTIONS.get(name, "")
    if not desc:
        parent_desc = PARENT_DESCRIPTIONS.get(parent_name, "")
        if parent_desc:
            desc = f"{parent_desc}の「{name}」サブモジュール"
        else:
            desc = f"'{name}' ディレクトリ"

    # Count contents
    py_files = list(dir_path.glob("*.py"))
    md_files = list(dir_path.glob("*.md"))
    subdirs = [d for d in dir_path.iterdir() if d.is_dir() and d.name not in SKIP_PATTERNS]
    all_files = [f for f in dir_path.iterdir() if f.is_file() and f.name != "PROOF.md"]

    lines = [
        f"# {name}/",
        "",
        f"> {desc}",
        "",
    ]

    # Content summary
    if py_files or all_files:
        lines.append("## 構成")
        lines.append("")
        if py_files:
            for pf in sorted(py_files):
                # Read first PURPOSE line if exists
                purpose = ""
                try:
                    content = pf.read_text(encoding="utf-8", errors="ignore")
                    for line in content.splitlines():
                        if line.strip().startswith("# PURPOSE:"):
                            purpose = line.strip().replace("# PURPOSE:", "").strip()
                            break
                except Exception:
                    pass
                if purpose:
                    lines.append(f"- **{pf.name}** — {purpose}")
                else:
                    lines.append(f"- **{pf.name}**")
        for f in sorted(all_files):
            if f.suffix != ".py" and f.name not in (".gitkeep", "__init__.py"):
                lines.append(f"- {f.name}")
        if subdirs:
            for sd in sorted(subdirs):
                lines.append(f"- `{sd.name}/`")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate PROOF.md for directories")
    parser.add_argument("root", help="Root directory to scan")
    parser.add_argument("--write", action="store_true", help="Actually write files")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"❌ Not a directory: {root}")
        sys.exit(1)

    generated = 0
    skipped = 0

    for dirpath in sorted(root.rglob("*")):
        if not dirpath.is_dir():
            continue
        if _should_skip(dirpath, root):
            skipped += 1
            continue
        if (dirpath / "PROOF.md").exists():
            continue

        content = _generate_proof_content(dirpath)
        rel = dirpath.relative_to(root)

        if args.write:
            (dirpath / "PROOF.md").write_text(content, encoding="utf-8")
            print(f"  ✅ {rel}/PROOF.md")
        else:
            print(f"  📋 {rel}/PROOF.md (preview)")
            for line in content.splitlines()[:5]:
                print(f"     {line}")
            print()

        generated += 1

    print(f"\n{'Wrote' if args.write else 'Would write'}: {generated} PROOF.md files")
    print(f"Skipped: {skipped} non-source dirs")


if __name__ == "__main__":
    main()
