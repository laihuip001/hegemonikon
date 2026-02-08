#!/usr/bin/env python3
# PROOF: [L2/ツール] <- scripts/
# PURPOSE: docstringと関数名から PURPOSE コメントを自動生成し、不足している関数に一括追加する
"""
PURPOSE Batch Adder — Docstring/名前から PURPOSE を推論して自動追加

Strategy:
1. docstring の第1文 → PURPOSE 候補を生成
2. docstring がなければ関数名から推論
3. 既に PURPOSE がある行はスキップ

Usage:
    python scripts/purpose_batch_add.py mekhane/           # dry-run
    python scripts/purpose_batch_add.py mekhane/ --write   # 実際に書き込み
    python scripts/purpose_batch_add.py mekhane/ --write --dir anamnesis  # 1ディレクトリのみ
"""

import argparse
import ast
import re
import sys
from pathlib import Path

# Skip patterns
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".venv", "node_modules", "models"}
SKIP_FILES = {"__init__.py"}

# PURPOSE pattern
PURPOSE_RE = re.compile(r"#\s*PURPOSE\s*:", re.IGNORECASE)


def _infer_purpose_from_docstring(docstring: str) -> str | None:
    """docstring の第1文から PURPOSE を生成する."""
    if not docstring:
        return None

    # 最初の意味のある行を取得
    lines = [l.strip() for l in docstring.strip().splitlines() if l.strip()]
    if not lines:
        return None

    first_line = lines[0]

    # 短すぎる or 長すぎる
    if len(first_line) < 5 or len(first_line) > 120:
        if len(first_line) > 120:
            first_line = first_line[:117] + "..."
        elif len(first_line) < 5:
            return None

    # 末尾のピリオドを除去
    first_line = first_line.rstrip(".")

    return first_line


def _infer_purpose_from_name(name: str, is_class: bool = False) -> str:
    """関数名/クラス名から PURPOSE を推論する."""
    # CamelCase → words
    if is_class:
        words = re.findall(r"[A-Z][a-z]*|[a-z]+", name)
        return " ".join(words).capitalize() + " の実装"

    # snake_case → words
    words = name.split("_")
    words = [w for w in words if w]

    # Common verb patterns
    verb_map = {
        "get": "を取得する",
        "set": "を設定する",
        "add": "を追加する",
        "create": "を生成する",
        "build": "を構築する",
        "make": "を作成する",
        "check": "を検証する",
        "validate": "を検証する",
        "parse": "を解析する",
        "load": "をロードする",
        "save": "を保存する",
        "run": "を実行する",
        "process": "を処理する",
        "update": "を更新する",
        "delete": "を削除する",
        "remove": "を除去する",
        "find": "を検索する",
        "search": "を検索する",
        "format": "をフォーマットする",
        "convert": "を変換する",
        "extract": "を抽出する",
        "collect": "を収集する",
        "init": "を初期化する",
        "setup": "をセットアップする",
        "cleanup": "をクリーンアップする",
        "close": "を閉じる",
        "open": "を開く",
        "read": "を読み取る",
        "write": "を書き込む",
        "send": "を送信する",
        "receive": "を受信する",
        "start": "を開始する",
        "stop": "を停止する",
        "reset": "をリセットする",
        "clear": "をクリアする",
        "flush": "をフラッシュする",
        "emit": "を発行する",
        "dispatch": "をディスパッチする",
        "register": "を登録する",
        "handle": "を処理する",
        "render": "をレンダリングする",
        "compute": "を計算する",
        "calculate": "を計算する",
        "estimate": "を推定する",
        "diagnose": "を診断する",
        "recommend": "を推薦する",
        "suggest": "を提案する",
        "classify": "を分類する",
        "embed": "をベクトル化する",
        "index": "をインデックスする",
        "ingest": "を取り込む",
        "export": "をエクスポートする",
        "import": "をインポートする",
        "merge": "をマージする",
        "split": "を分割する",
        "sort": "をソートする",
        "filter": "をフィルタする",
        "map": "をマッピングする",
        "reduce": "を集約する",
        "transform": "を変換する",
        "normalize": "を正規化する",
        "test": "をテストする",
        "verify": "を検証する",
        "assert": "を表明する",
        "log": "を記録する",
        "print": "を出力する",
        "display": "を表示する",
        "show": "を表示する",
    }

    if words and words[0].lower() in verb_map:
        verb = words[0].lower()
        obj = "_".join(words[1:]) if len(words) > 1 else name
        return f"{obj} {verb_map[verb]}"

    return f"{name} の処理"


def process_file(filepath: Path, write: bool = False) -> tuple[int, int]:
    """ファイルを処理して PURPOSE を追加する.

    Returns:
        (added_count, skipped_count)
    """
    try:
        source = filepath.read_text(encoding="utf-8")
    except Exception:
        return 0, 0

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0, 0

    lines = source.splitlines(keepends=True)
    insertions: list[tuple[int, str]] = []  # (line_number_0based, purpose_text)

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue

        name = node.name

        # Skip private/dunder
        if name.startswith("_"):
            continue

        # Check if PURPOSE already exists in the lines above the function
        has_purpose = False
        start_line = node.lineno - 1  # 0-based

        # Search upward from the function definition (up to 5 lines)
        search_start = max(0, start_line - 5)
        for check_line in range(search_start, start_line + 1):
            if check_line < len(lines) and PURPOSE_RE.search(lines[check_line]):
                has_purpose = True
                break

        if has_purpose:
            continue

        # Get docstring
        docstring = ast.get_docstring(node) or ""

        # Infer PURPOSE
        is_class = isinstance(node, ast.ClassDef)
        purpose = _infer_purpose_from_docstring(docstring)
        if not purpose:
            purpose = _infer_purpose_from_name(name, is_class=is_class)

        # Find insertion point (just before the def/class line)
        # Account for decorators
        if node.decorator_list:
            insert_line = node.decorator_list[0].lineno - 1  # before first decorator
        else:
            insert_line = start_line

        insertions.append((insert_line, purpose))

    if not insertions:
        return 0, 0

    if not write:
        for line_num, purpose_text in insertions:
            rel = filepath.relative_to(filepath.parent.parent) if filepath.parent.parent.exists() else filepath.name
            print(f"  📋 {rel}:{line_num + 1} → # PURPOSE: {purpose_text}")
        return len(insertions), 0

    # Apply insertions (reverse order to maintain line numbers)
    insertions.sort(key=lambda x: x[0], reverse=True)
    for line_num, purpose_text in insertions:
        # Get indentation from the target line
        target_line = lines[line_num] if line_num < len(lines) else ""
        indent = len(target_line) - len(target_line.lstrip())
        indent_str = " " * indent

        purpose_line = f"{indent_str}# PURPOSE: {purpose_text}\n"
        lines.insert(line_num, purpose_line)

    filepath.write_text("".join(lines), encoding="utf-8")
    return len(insertions), 0


def main():
    parser = argparse.ArgumentParser(description="PURPOSE Batch Adder")
    parser.add_argument("root", help="Root directory to scan")
    parser.add_argument("--write", action="store_true", help="Actually write files")
    parser.add_argument("--dir", type=str, help="Only process this subdirectory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"❌ Not a directory: {root}")
        sys.exit(1)

    total_added = 0
    total_files = 0

    for filepath in sorted(root.rglob("*.py")):
        # Skip patterns
        if any(part in SKIP_DIRS for part in filepath.parts):
            continue
        if filepath.name in SKIP_FILES:
            continue
        if args.dir and args.dir not in str(filepath):
            continue

        added, _ = process_file(filepath, write=args.write)
        if added > 0:
            total_files += 1
            total_added += added

    action = "Added" if args.write else "Would add"
    print(f"\n{action}: {total_added} PURPOSE annotations across {total_files} files")


if __name__ == "__main__":
    main()
