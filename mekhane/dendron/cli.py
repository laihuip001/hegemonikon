# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/dendron/  # noqa: AI-022
"""
Dendron CLI — コマンドラインインターフェース

Usage:
    python -m mekhane.dendron.cli check [PATH] [--coverage] [--ci] [--format FORMAT]
    python -m mekhane.dendron.cli purpose [PATH] [--ci] [--strict]
"""

import argparse
import sys
from pathlib import Path

from .checker import DendronChecker, ProofStatus
from .reporter import DendronReporter, ReportFormat


# PURPOSE: Dendron CLI のメインエントリポイントとサブコマンド振り分け
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

    # purpose コマンド (v2.6)
    purpose_parser = subparsers.add_parser("purpose", help="L2 Purpose 品質チェック")
    purpose_parser.add_argument(
        "path", nargs="?", default=".", help="チェック対象ディレクトリ (default: .)"
    )
    purpose_parser.add_argument("--ci", action="store_true", help="CI モード (WEAK/MISSING で exit 1)")
    purpose_parser.add_argument(
        "--strict", action="store_true",
        help="厳密モード: WEAK も FAIL 扱い"
    )

    args = parser.parse_args()

    if args.command == "check":
        return cmd_check(args)
    elif args.command == "purpose":
        return cmd_purpose(args)

    return 0


# PURPOSE: check コマンドの実行とレポート出力
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


# PURPOSE: L2 Purpose 品質チェックを実行し、WEAK/MISSING を報告する
def cmd_purpose(args):  # noqa: AI-005
    """purpose コマンドの実行 (v2.6)"""
    path = Path(args.path)

    if not path.exists():
        print(f"Error: {path} が存在しません", file=sys.stderr)
        return 1

    checker = DendronChecker(check_dirs=False, check_files=True, check_functions=True)
    result = checker.check(path)

    ok = sum(1 for f in result.function_proofs if f.status == ProofStatus.OK)
    weak = [f for f in result.function_proofs if f.status == ProofStatus.WEAK]
    missing = [f for f in result.function_proofs if f.status == ProofStatus.MISSING]
    exempt = sum(1 for f in result.function_proofs if f.status == ProofStatus.EXEMPT)

    total = ok + len(weak) + len(missing)
    coverage = (ok / total * 100) if total > 0 else 100.0

    if args.ci:
        # CI 出力
        status = "✅" if len(missing) == 0 and (not args.strict or len(weak) == 0) else "❌"
        print(f"{status} Purpose: {ok}/{total} OK ({coverage:.1f}%), {len(weak)} weak, {len(missing)} missing")
        if weak and args.strict:
            for f in weak[:5]:
                print(f"  ⚠️ {f.path}:{f.line_number} {f.name} — {f.quality_issue}")
        if missing:
            for f in missing[:5]:
                print(f"  ❌ {f.path}:{f.line_number} {f.name}")

        # 判定
        if len(missing) > 0:
            return 1
        if args.strict and len(weak) > 0:
            return 1
        return 0
    else:
        # テキスト出力
        print(f"=== L2 Purpose Check (v2.6) ===")
        print(f"OK: {ok} | WEAK: {len(weak)} | MISSING: {len(missing)} | EXEMPT: {exempt}")
        print(f"Coverage: {coverage:.1f}%")

        if weak:
            print()
            print("⚠️ WEAK Purposes (WHAT not WHY):")
            for f in weak:
                print(f"  {f.path}:{f.line_number} {f.name}")
                print(f"    Current: {f.purpose_text}")
                print(f"    Issue:   {f.quality_issue}")

        if missing:
            print()
            print("❌ MISSING Purposes:")
            for f in missing[:20]:
                print(f"  {f.path}:{f.line_number} {f.name}")
            if len(missing) > 20:
                print(f"  ... and {len(missing) - 20} more")

        print()
        if len(weak) == 0 and len(missing) == 0:
            print("✅ ALL CLEAR")
        else:
            print(f"❌ {len(weak)} WEAK + {len(missing)} MISSING to fix")

        return 0


if __name__ == "__main__":
    sys.exit(main())

