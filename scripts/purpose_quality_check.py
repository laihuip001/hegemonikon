#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/
# PURPOSE: 形骸化PURPOSE注釈を検出し、品質改善の対象を特定する
"""
PURPOSE Quality Checker — 形骸化PURPOSE検出

PROOF: [L3/ユーティリティ]

P3 → コード品質基準の維持が必要
   → PURPOSE注釈が形骸化するリスクがある
   → 自動検出で劣化を早期発見する

REASON: /bou ⑤「美しいコード基準の維持・強化」から生成。
        144個の形骸化PURPOSEが発見され、自動検出が必要と判断。

Q.E.D.

Usage:
    python scripts/purpose_quality_check.py [--fix-hint] [path]
"""

import re
import sys
from pathlib import Path

# 形骸化パターン: 意味のないPURPOSE注釈
DEGENERATE_PATTERNS = [
    (r"# PURPOSE: 内部処理: init__", "WHY does this class exist?"),
    (r"# PURPOSE: 内部処理: repr__", "WHY is this repr format chosen?"),
    (r"# PURPOSE: 内部処理: str__", "WHY is this str format chosen?"),
    (r"# PURPOSE: 内部処理: (\w+)", "WHY does this internal method exist?"),
    (r"# PURPOSE: 関数: (\w+)", "WHAT problem does this function solve?"),
    (r"# PURPOSE: 取得: (\w+)", "WHY is this property needed?"),
]


def check_file(filepath: Path) -> list[dict]:
    """Check a single file for degenerate PURPOSE annotations."""
    issues = []
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, PermissionError):
        return issues

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        for pattern, hint in DEGENERATE_PATTERNS:
            if re.match(pattern, stripped):
                issues.append({
                    "file": str(filepath),
                    "line": i,
                    "content": stripped,
                    "hint": hint,
                })
                break

    return issues


def main():
    fix_hint = "--fix-hint" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    search_path = Path(args[0]) if args else Path("mekhane")

    if not search_path.exists():
        print(f"Path not found: {search_path}")
        sys.exit(1)

    py_files = (
        [search_path] if search_path.is_file()
        else sorted(search_path.rglob("*.py"))
    )

    total_issues = 0
    file_issues: dict[str, list] = {}

    for f in py_files:
        if "__pycache__" in str(f) or "_limbo" in str(f):
            continue
        issues = check_file(f)
        if issues:
            file_issues[str(f)] = issues
            total_issues += len(issues)

    if not file_issues:
        print("✅ No degenerate PURPOSE annotations found.")
        sys.exit(0)

    # Output
    print(f"⚠️  {total_issues} degenerate PURPOSE annotations found in {len(file_issues)} files\n")

    for filepath, issues in sorted(file_issues.items()):
        print(f"  {filepath} ({len(issues)} issues)")
        if fix_hint:
            for issue in issues:
                print(f"    L{issue['line']}: {issue['content']}")
                print(f"           → Hint: {issue['hint']}")

    print(f"\nTotal: {total_issues} degenerate / {sum(len(list(Path(p).parent.rglob('*.py'))) for p in file_issues) if False else '?'} files checked")
    print("Run with --fix-hint to see improvement suggestions per line.")


if __name__ == "__main__":
    main()
