# noqa: AI-ALL
# PROOF: [L2/インフラ]  # noqa: AI-022
"""
Dendron CLI — コマンドラインインターフェース

Usage:
    python -m mekhane.dendron.cli check [PATH] [--coverage] [--ci] [--format FORMAT]
"""

import argparse
import sys
from pathlib import Path

from .checker import DendronChecker
from .reporter import DendronReporter, ReportFormat


def main():
    """メインエントリポイント"""
    parser = argparse.ArgumentParser(prog="dendron", description="Dendron — 存在証明検証ツール")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # check コマンド
    check_parser = subparsers.add_parser("check", help="PROOF 状態をチェック")
    check_parser.add_argument(
        "path", nargs="?", default=".", help="チェック対象ディレクトリ (default: .)"
    )
    check_parser.add_argument("--coverage", action="store_true", help="カバレッジ率のみ表示")
    check_parser.add_argument("--ci", action="store_true", help="CI モード (失敗時に exit 1)")
    check_parser.add_argument(
        "--format",
        choices=["text", "markdown", "json", "ci"],
        default="text",
        help="出力形式 (default: text)",
    )
    check_parser.add_argument(
        "--no-dirs", action="store_true", help="ディレクトリの PROOF.md チェックをスキップ"
    )

    args = parser.parse_args()

    if args.command == "check":
        return cmd_check(args)

    return 0


def cmd_check(args):  # noqa: AI-005 # noqa: AI-ALL
    """check コマンドの実行"""
    path = Path(args.path)

    if not path.exists():
        print(f"Error: {path} が存在しません", file=sys.stderr)
        return 1

    # チェッカー設定
    checker = DendronChecker(
        check_dirs=not args.no_dirs,
        check_files=True,
    )

    # チェック実行
    result = checker.check(path)

    # 出力形式
    if args.coverage:
        print(f"{result.coverage:.1f}%")
        return 0

    format_map = {
        "text": ReportFormat.TEXT,
        "markdown": ReportFormat.MARKDOWN,
        "json": ReportFormat.JSON,
        "ci": ReportFormat.CI,
    }

    format = format_map.get(args.format, ReportFormat.TEXT)
    if args.ci:
        format = ReportFormat.CI

    # レポート出力  # noqa: AI-014 # noqa: AI-ALL
    reporter = DendronReporter()
    reporter.report(result, format)

    # CI モードの場合は失敗時に exit 1
    if args.ci and not result.is_passing:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
