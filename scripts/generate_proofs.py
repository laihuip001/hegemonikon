#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/
# PURPOSE: PROOF.md の自動生成と存在証明の機械的担保
"""Batch-generate PROOF.md for directories that have Python files but no PROOF.md.

Uses heuristics (directory name, parent's PROOF.md, Python files) to generate
PURPOSE and REASON fields without LLM.
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Directories to skip
SKIP_PATTERNS = {
    "tests", "__pycache__", ".git", ".venv", "node_modules",
    "_limbo", ".codex", "experiments", ".agent/scripts",
}

# Human curated PURPOSE/REASON for known directories
KNOWN = {
    "hermeneus/src": (
        "解釈エンジンの中核ソースコード",
        "認知解釈の具体実装が必要だった",
    ),
    "mekhane/anamnesis/collectors": (
        "外部知識源からデータを収集するコレクタモジュール群",
        "Gnōsis に多様なデータソースを統合する必要があった",
    ),
    "mekhane/anamnesis/models": (
        "知識構造のデータモデル定義",
        "論文・知識アイテムの型安全な表現が必要だった",
    ),
    "mekhane/ccl/guardrails": (
        "CCL 式のバリデーションとガードレール",
        "不正な CCL 式を実行前に検出・拒否する安全機構が必要だった",
    ),
    "mekhane/ccl/learning": (
        "CCL の学習・パターン抽出機能",
        "使用パターンから CCL 式を自動改善する機構が必要だった",
    ),
    "mekhane/ergasterion/digestor": (
        "外部コンテンツを Hegemonikón に消化する変換エンジン",
        "外部知識を内部形式に変換する統一インターフェースが必要だった",
    ),
    "mekhane/ergasterion/typos": (
        "プロンプト言語の解析・実行エンジン",
        "構造化されたプロンプト記法の機械的処理が必要だった",
    ),
    "mekhane/ergasterion/synedrion": (
        "偉人評議会（多視点批評）の実行エンジン",
        "複数の仮想知性による多角的評価の自動実行が必要だった",
    ),
    "mekhane/peira/scripts": (
        "テスト・実験用ユーティリティスクリプト",
        "peira モジュールの動作検証用スクリプトが必要だった",
    ),
    "mekhane/pks/links": (
        "PKS エンジンのリンク管理モジュール",
        "知識構造間の関連性を追跡・管理する機構が必要だった",
    ),
    "mekhane/poiema/flow": (
        "ワークフロー実行のフロー制御エンジン",
        "複雑なワークフロー手順の逐次・並列実行管理が必要だった",
    ),
    "mekhane/symploke/adapters": (
        "外部 API との接続アダプタ群",
        "Jules/n8n 等の外部サービスとの統一的接続層が必要だった",
    ),
    "mekhane/symploke/indices": (
        "インデックス構築・管理モジュール",
        "知識ベースの高速検索のためのインデックス管理が必要だった",
    ),
    "mekhane/symploke/search": (
        "セマンティック検索エンジン",
        "ベクトル類似度によるコンテキスト検索が必要だった",
    ),
    "mekhane/synteleia/dokimasia": (
        "品質検査・バリデーション実行エンジン",
        "コード品質の自動検査とレポーティングが必要だった",
    ),
    "mekhane/synteleia/poiesis": (
        "コード生成・変換エンジン",
        "テンプレートベースのコード自動生成が必要だった",
    ),
    "scripts": (
        "プロジェクト全体のユーティリティスクリプト群",
        "boot/bye/daily/export 等の運用スクリプトを一箇所に集約する必要があった",
    ),
}

TEMPLATE = """# PROOF.md — 存在証明書

PURPOSE: {purpose}
REASON: {reason}

> **∃ {dirname}/** — この場所は存在しなければならない

---

## 公理

1. **存在公理**: このディレクトリは `{parent_purpose}` の一部として存在が要請される
2. **機能公理**: `{purpose}` を実現するファイル群がここに配置される

## ファイル構成

{file_list}

---

*Generated: 2026-02-08 by generate_proofs.py*
"""


def find_eligible_dirs() -> list[Path]:
    """PROOF.md がないが Python ファイルがあるディレクトリを検索"""
    py_dirs = set()
    for py_file in PROJECT_ROOT.rglob("*.py"):
        rel = py_file.parent.relative_to(PROJECT_ROOT)
        skip = any(part in SKIP_PATTERNS for part in rel.parts)
        if not skip:
            py_dirs.add(rel)

    eligible = []
    for d in sorted(py_dirs):
        proof = PROJECT_ROOT / d / "PROOF.md"
        if not proof.exists():
            eligible.append(d)
    return eligible


def get_parent_purpose(dir_path: Path) -> str:
    """親ディレクトリの PROOF.md から PURPOSE を取得"""
    parent = dir_path.parent
    while parent != Path("."):
        proof = PROJECT_ROOT / parent / "PROOF.md"
        if proof.exists():
            text = proof.read_text(encoding="utf-8")
            m = re.search(r"PURPOSE:\s*(.+)", text)
            if m:
                return m.group(1).strip()
        parent = parent.parent
    return "Hegemonikón プロジェクト"


def generate_proof(dir_path: Path, dry_run: bool = False) -> str:
    """PROOF.md を生成"""
    rel_str = str(dir_path)
    dirname = dir_path.name

    if rel_str in KNOWN:
        purpose, reason = KNOWN[rel_str]
    else:
        purpose = f"{dirname} モジュールの実装"
        reason = f"{dirname} の機能が必要だった"

    parent_purpose = get_parent_purpose(dir_path)

    # ファイル一覧
    full_dir = PROJECT_ROOT / dir_path
    py_files = sorted(full_dir.glob("*.py"))
    file_list = "\n".join(
        f"| `{f.name}` | {_infer_file_purpose(f)} |"
        for f in py_files
    )
    if file_list:
        file_list = "| ファイル | 役割 |\n|:---------|:-----|\n" + file_list
    else:
        file_list = "(Python ファイルなし)"

    content = TEMPLATE.format(
        purpose=purpose,
        reason=reason,
        dirname=dirname,
        parent_purpose=parent_purpose,
        file_list=file_list,
    )

    target = full_dir / "PROOF.md"
    if dry_run:
        print(f"  [DRY-RUN] Would write: {target}")
    else:
        target.write_text(content, encoding="utf-8")
        print(f"  ✅ Created: {target.relative_to(PROJECT_ROOT)}")

    return content


def _infer_file_purpose(py_path: Path) -> str:
    """Python ファイルの先頭 docstring から目的を推定"""
    try:
        text = py_path.read_text(encoding="utf-8")[:500]
        # """docstring""" パターン
        m = re.search(r'"""(.+?)"""', text, re.DOTALL)
        if m:
            first_line = m.group(1).strip().split("\n")[0][:60]
            return first_line
        # # コメント
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("#") and not line.startswith("#!"):
                return line.lstrip("# ")[:60]
        return py_path.stem
    except Exception:
        return py_path.stem


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch-generate PROOF.md")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    eligible = find_eligible_dirs()
    print(f"=== PROOF.md Generator ===")
    print(f"Eligible directories: {len(eligible)}")
    print()

    for d in eligible:
        print(f"--- {d} ---")
        generate_proof(d, dry_run=args.dry_run)

    print(f"\n{'=' * 40}")
    mode = "DRY-RUN" if args.dry_run else "GENERATED"
    print(f"✅ {mode}: {len(eligible)} PROOF.md files")


if __name__ == "__main__":
    main()
