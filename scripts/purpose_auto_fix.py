#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/
# PURPOSE: 形骸化PURPOSEの一括修正 — コンテキスト理解による自動置換
"""
PURPOSE Auto-Fixer — 形骸化PURPOSEを文脈から推測して修正する

Approach:
    1. 形骸化パターンを検出
    2. 前後のコンテキスト（class名、docstring、関数名、ファイルパス）を読む
    3. テンプレートベースで meaningful な PURPOSE を生成
    4. --dry-run でプレビュー、--apply で実際に置換

Usage:
    python scripts/purpose_auto_fix.py mekhane/ --dry-run   # プレビュー
    python scripts/purpose_auto_fix.py mekhane/ --apply      # 実際に修正
"""

import argparse
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Detection patterns (same as purpose_quality_check.py)
# ---------------------------------------------------------------------------

DEGENERATE_PATTERNS = [
    re.compile(r"^(\s*)# PURPOSE: 内部処理: init__\s*$"),
    re.compile(r"^(\s*)# PURPOSE: 内部処理: repr__\s*$"),
    re.compile(r"^(\s*)# PURPOSE: 内部処理: str__\s*$"),
    re.compile(r"^(\s*)# PURPOSE: 内部処理: (\w+)\s*$"),
    re.compile(r"^(\s*)# PURPOSE: 関数: (\w+)\s*$"),
    re.compile(r"^(\s*)# PURPOSE: 取得: (\w+)\s*$"),
]


# ---------------------------------------------------------------------------
# Context extraction
# ---------------------------------------------------------------------------


def _find_class_name(lines: list[str], line_idx: int) -> str | None:
    """Find the class name that this line belongs to."""
    for i in range(line_idx + 1, min(line_idx + 5, len(lines))):
        m = re.match(r"\s*class (\w+)", lines[i])
        if m:
            return m.group(1)
    # Search backwards for enclosing class
    indent = len(lines[line_idx]) - len(lines[line_idx].lstrip())
    for i in range(line_idx - 1, max(0, line_idx - 50), -1):
        m = re.match(r"(\s*)class (\w+)", lines[i])
        if m and len(m.group(1)) < indent:
            return m.group(2)
    return None


def _find_func_name(lines: list[str], line_idx: int) -> str | None:
    """Find the function name immediately following this line."""
    for i in range(line_idx + 1, min(line_idx + 3, len(lines))):
        m = re.match(r"\s*def (\w+)", lines[i])
        if m:
            return m.group(1)
    return None


def _find_docstring(lines: list[str], line_idx: int) -> str | None:
    """Find the docstring of the function/class following this line."""
    for i in range(line_idx + 1, min(line_idx + 10, len(lines))):
        stripped = lines[i].strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            # Single-line docstring
            if stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                return stripped.strip("\"'").strip()
            # Multi-line: collect until closing
            doc = [stripped.strip("\"'").strip()]
            for j in range(i + 1, min(i + 5, len(lines))):
                if '"""' in lines[j] or "'''" in lines[j]:
                    doc.append(lines[j].strip().strip("\"'").strip())
                    break
                doc.append(lines[j].strip())
            return " ".join(d for d in doc if d)[:80]
    return None


def _get_module_purpose(filepath: Path) -> str:
    """Get module-level purpose from file header."""
    try:
        content = filepath.read_text(encoding="utf-8")
        for line in content.splitlines()[:20]:
            if line.strip().startswith("# PURPOSE:") and "関数" not in line and "内部処理" not in line:
                return line.split("# PURPOSE:", 1)[1].strip()
    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# Smart replacement generators
# ---------------------------------------------------------------------------

# Module path → domain hint
_DOMAIN_HINTS = {
    "anamnesis": "知識基盤",
    "ccl": "CCL認知代数",
    "dendron": "存在証明",
    "ergasterion": "自動化基盤",
    "fep": "FEP推論",
    "mcp": "MCPサービス",
    "peira": "データパイプライン",
    "pks": "知識プッシュ",
    "poiema": "生成エンジン",
    "scripts": "運用ツール",
    "symploke": "統合レイヤー",
}


def _domain_from_path(filepath: Path) -> str:
    parts = filepath.parts
    for p in parts:
        if p in _DOMAIN_HINTS:
            return _DOMAIN_HINTS[p]
    return "システム"


def generate_replacement(
    line: str, lines: list[str], line_idx: int, filepath: Path
) -> str | None:
    """Generate a meaningful PURPOSE replacement based on context."""
    indent = len(line) - len(line.lstrip())
    prefix = " " * indent + "# PURPOSE: "
    domain = _domain_from_path(filepath)
    class_name = _find_class_name(lines, line_idx)
    func_name = _find_func_name(lines, line_idx)
    docstring = _find_docstring(lines, line_idx)

    # Pattern: init__
    if "init__" in line:
        if class_name:
            if docstring:
                return f"{prefix}{class_name} の初期化 — {docstring}"
            return f"{prefix}{class_name} の構成と依存関係の初期化"
        return f"{prefix}{domain}コンポーネントの初期化"

    # Pattern: repr__ / str__
    if "repr__" in line:
        return f"{prefix}デバッグ・ログ出力での視認性確保"
    if "str__" in line:
        return f"{prefix}ユーザー向け可読表現の生成"

    # Pattern: 関数: main
    if re.search(r"関数: main\b", line):
        module_purpose = _get_module_purpose(filepath)
        if module_purpose:
            return f"{prefix}CLI エントリポイント — {module_purpose}"
        return f"{prefix}CLI エントリポイント — {domain}の直接実行"

    # Pattern: 関数: xxx
    m = re.search(r"関数: (\w+)", line)
    if m:
        fname = m.group(1)
        if docstring:
            return f"{prefix}{docstring}"
        # Common function names
        name_hints = {
            "clear": "状態のリセットと再初期化",
            "close": "リソースの解放とクリーンアップ",
            "save": "永続化 — 状態をディスクに保存",
            "load": "永続化された状態の復元",
            "search": "セマンティック検索の実行",
            "embed": "テキストをベクトル空間に射影",
            "embed_batch": "複数テキストの一括ベクトル化",
            "add_papers": "論文データのインデックスへの追加",
            "stats": "インデックスの統計情報を集計",
            "format": "構造化データを可読形式に変換",
            "to_dict": "シリアライズ用辞書への変換",
            "from_dict": "辞書からのデシリアライズ・復元",
            "run": "メイン処理の実行",
            "validate": "入力の整合性検証",
            "parse": "テキスト解析と構造化",
            "collect": "データソースからの収集",
            "turn_count": "対話ターン数の取得（コンテキスト管理用）",
        }
        if fname in name_hints:
            return f"{prefix}{name_hints[fname]}"
        return f"{prefix}{fname} — {domain}の処理"

    # Pattern: 取得: xxx
    m = re.search(r"取得: (\w+)", line)
    if m:
        pname = m.group(1)
        if docstring:
            return f"{prefix}{docstring}"
        name_hints = {
            "get_stats": "インデックス統計の取得（ヘルスチェック用）",
            "get_embedder": "埋め込みモデルの遅延初期化と取得",
        }
        if pname in name_hints:
            return f"{prefix}{name_hints[pname]}"
        return f"{prefix}{pname} プロパティの取得"

    # Pattern: 内部処理: xxx (catch-all)
    m = re.search(r"内部処理: (\w+)", line)
    if m:
        method = m.group(1)
        name_hints = {
            "load": "永続化された状態の復元",
            "save": "状態のディスク永続化",
        }
        if method in name_hints:
            return f"{prefix}{name_hints[method]}"
        if docstring:
            return f"{prefix}{docstring}"
        return f"{prefix}{method} — {domain}の内部処理"

    return None


# ---------------------------------------------------------------------------
# File processor
# ---------------------------------------------------------------------------


def process_file(filepath: Path, apply: bool = False) -> list[dict]:
    """Process a single file and optionally fix degenerate PURPOSEs."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return []

    lines = content.splitlines()
    fixes = []
    modified = False

    for i, line in enumerate(lines):
        for pattern in DEGENERATE_PATTERNS:
            if pattern.match(line):
                replacement = generate_replacement(line, lines, i, filepath)
                if replacement:
                    fixes.append({
                        "file": str(filepath),
                        "line": i + 1,
                        "old": line.rstrip(),
                        "new": replacement.rstrip(),
                    })
                    if apply:
                        lines[i] = replacement.rstrip()
                        modified = True
                break  # Only match first pattern

    if apply and modified:
        filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return fixes


def main():
    parser = argparse.ArgumentParser(description="PURPOSE Auto-Fixer")
    parser.add_argument("path", help="Directory or file to process")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--apply", action="store_true", help="Apply fixes")
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"❌ Not found: {target}")
        sys.exit(1)

    files = sorted(target.rglob("*.py")) if target.is_dir() else [target]

    total_fixes = 0
    for f in files:
        fixes = process_file(f, apply=args.apply)
        if fixes:
            rel = f.relative_to(Path.cwd()) if f.is_relative_to(Path.cwd()) else f
            print(f"\n{'✅' if args.apply else '📝'} {rel} ({len(fixes)} fixes)")
            for fix in fixes:
                print(f"  L{fix['line']}:")
                print(f"    - {fix['old'].strip()}")
                print(f"    + {fix['new'].strip()}")
            total_fixes += len(fixes)

    action = "applied" if args.apply else "would fix"
    print(f"\n{'✅' if args.apply else '📝'} Total: {total_fixes} {action}")


if __name__ == "__main__":
    main()
