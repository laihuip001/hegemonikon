# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/dendron/  # noqa: AI-022
"""
Dendron CLI — コマンドラインインターフェース

Usage:
    python -m mekhane.dendron.cli check [PATH] [--coverage] [--ci] [--format FORMAT]
    python -m mekhane.dendron.cli purpose [PATH] [--ci] [--strict]
    python -m mekhane.dendron.cli variables [PATH] [--ci]
    python -m mekhane.dendron.cli skill-audit [AGENT_DIR] [--ci] [--boot-summary]
"""

import argparse
import sys
from pathlib import Path

from .checker import DendronChecker, ProofStatus, VariableProof
from .reporter import DendronReporter, ReportFormat


# PURPOSE: Dendron CLI のメインエントリポイントとサブコマンド振り分け
def main() -> int:
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
    check_parser.add_argument(
        "--ept", action="store_true", help="EPT フルマトリクス (NF2/NF3/BCNF) を有効化"
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

    # variables コマンド (v3.0)
    var_parser = subparsers.add_parser("variables", help="L3 Variable 品質チェック (型ヒスト + 命名)")
    var_parser.add_argument(
        "path", nargs="?", default=".", help="チェック対象ディレクトリ (default: .)"
    )
    var_parser.add_argument("--ci", action="store_true", help="CI モード")

    # skill-audit コマンド (v3.1: Safety Contract 検証)
    audit_parser = subparsers.add_parser("skill-audit", help="Safety Contract + lcm_state 検証")
    audit_parser.add_argument(
        "agent_dir", nargs="?", default=".agent", help=".agent/ ディレクトリ (default: .agent)"
    )
    audit_parser.add_argument("--ci", action="store_true", help="CI モード (error で exit 1)")
    audit_parser.add_argument("--verbose", "-v", action="store_true", help="OK も表示")
    audit_parser.add_argument("--boot-summary", action="store_true", help="/boot 用コンパクト出力")

    # diff コマンド (v3.3: EPT 差分検出)
    diff_parser = subparsers.add_parser("diff", help="Git diff に基づく EPT 変化検出")
    diff_parser.add_argument(
        "path", nargs="?", default=".", help="プロジェクトルート (default: .)"
    )
    diff_parser.add_argument(
        "--since", default="HEAD~1", help="比較起点 (default: HEAD~1)"
    )

    # guard コマンド (v3.6: アンチウイルス — 変更ファイルのみチェック)
    guard_parser = subparsers.add_parser("guard", help="変更ファイルのみ PROOF/PURPOSE/REASON をチェック")
    guard_parser.add_argument(
        "path", nargs="?", default=".", help="プロジェクトルート (default: .)"
    )
    guard_parser.add_argument(
        "--since", default=None,
        help="比較起点 (default: ステージ済み + 未コミット変更)"
    )

    args = parser.parse_args()

    if args.command == "check":
        return cmd_check(args)
    elif args.command == "purpose":
        return cmd_purpose(args)
    elif args.command == "variables":
        return cmd_variables(args)
    elif args.command == "skill-audit":
        return cmd_skill_audit(args)
    elif args.command == "diff":
        return cmd_diff(args)
    elif args.command == "guard":
        return cmd_guard(args)

    return 0


# PURPOSE: check コマンドの実行とレポート出力
def cmd_check(args: argparse.Namespace) -> int:  # noqa: AI-005 # noqa: AI-ALL
    """check コマンドの実行"""
    path = Path(args.path)

    if not path.exists():
        print(f"Error: {path} が存在しません", file=sys.stderr)
        return 1

    # チェッカー設定
    checker = DendronChecker(
        check_dirs=not args.no_dirs,
        check_files=True,
        check_structure=getattr(args, 'ept', False),
        check_function_nf=getattr(args, 'ept', False),
        check_verification=getattr(args, 'ept', False),
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
def cmd_purpose(args: argparse.Namespace) -> int:  # noqa: AI-005
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


# PURPOSE: L3 Variable 品質チェック (型ヒストカバレッジ) を実行する
def cmd_variables(args: argparse.Namespace) -> int:  # noqa: AI-005
    """variables コマンドの実行 (v3.0)"""
    path = Path(args.path)

    if not path.exists():
        print(f"Error: {path} が存在しません", file=sys.stderr)
        return 1

    checker = DendronChecker(check_dirs=False, check_files=True, check_functions=False, check_variables=True)
    result = checker.check(path)

    hints_total = result.total_checked_signatures
    hints_ok = result.signatures_with_hints
    hints_missing = result.signatures_missing_hints
    short = result.short_name_violations
    hint_cov = (hints_ok / hints_total * 100) if hints_total > 0 else 100.0

    if args.ci:
        short_str = f", {short} short" if short > 0 else ""
        status = "✅" if hints_missing == 0 and short == 0 else "⚠️"
        print(f"{status} TypeHints: {hints_ok}/{hints_total} ({hint_cov:.0f}%){short_str}")
        if hints_missing > 0:
            missing_proofs = [v for v in result.variable_proofs if v.check_type == "type_hint" and v.status == ProofStatus.MISSING]
            for v in missing_proofs[:5]:
                print(f"  ❌ {v.path}:{v.line_number} {v.name} — {v.reason}")
        return 0  # warn only for now
    else:
        print(f"=== L3 Variable Check (v3.0) ===")
        print(f"Type Hints: {hints_ok}/{hints_total} ({hint_cov:.1f}%)")
        print(f"Short name violations: {short}")
        print()
        if hints_missing > 0:
            print("❌ Missing type hints:")
            missing_proofs = [v for v in result.variable_proofs if v.check_type == "type_hint" and v.status == ProofStatus.MISSING]
            for v in missing_proofs[:20]:
                print(f"  {v.path}:{v.line_number} {v.name}")
            if len(missing_proofs) > 20:
                print(f"  ... and {len(missing_proofs) - 20} more")
        if short > 0:
            print("⚠️ Short name violations:")
            short_proofs = [v for v in result.variable_proofs if v.check_type == "short_name"]
            for v in short_proofs:
                print(f"  {v.path}:{v.line_number} {v.name} — {v.reason}")
        if hints_missing == 0 and short == 0:
            print("✅ ALL CLEAR")
        return 0


# PURPOSE: Safety Contract (risk_tier/lcm_state) の検証を実行し、レポートを出力する
def cmd_skill_audit(args: argparse.Namespace) -> int:  # noqa: AI-005
    """skill-audit コマンドの実行 (v3.1: Safety Contract)"""
    from .skill_checker import run_audit, format_report

    agent_dir = Path(args.agent_dir)
    if not agent_dir.exists():
        print(f"Error: {agent_dir} が存在しません", file=sys.stderr)
        return 1

    result = run_audit(agent_dir)

    if args.boot_summary:
        # /boot 用コンパクトサマリ
        dist = result.risk_distribution()
        lcm = result.lcm_distribution()
        print(f"\n🛡️ Safety Contract:")
        print(f"  Skills: {result.skills_checked} | WF: {result.workflows_checked}")
        risk_parts = [f"{k}:{v}" for k, v in dist.items() if v > 0]
        if risk_parts:
            print(f"  Risk: {' '.join(risk_parts)}")
        lcm_parts = [f"{k}:{v}" for k, v in lcm.items() if v > 0]
        if lcm_parts:
            print(f"  LCM:  {' '.join(lcm_parts)}")
        if result.errors > 0:
            print(f"  ⚠️ {result.errors} errors found")
    else:
        print(format_report(result, verbose=getattr(args, 'verbose', False)))

    if args.ci and not result.is_passing:
        return 1

    return 0


# PURPOSE: Git diff に基づく EPT 変化検出コマンド (v3.3)
def cmd_diff(args: argparse.Namespace) -> int:
    """diff コマンドの実行"""
    from .diff import diff_check, format_diff_result

    root = Path(args.path).resolve()
    result = diff_check(root, since=args.since)
    print(format_diff_result(result))
    return 0


# PURPOSE: 変更ファイルのみ PROOF/PURPOSE/REASON をチェックする (v3.6 アンチウイルス)
def cmd_guard(args: argparse.Namespace) -> int:
    """guard コマンドの実行 — 変更ファイルのみ高速チェック"""
    import subprocess as _sp

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Error: {root} が存在しません", file=sys.stderr)
        return 1

    # 1. 変更ファイルを取得
    since = args.since
    if since:
        # 明示的な比較起点
        cmd = ["git", "diff", "--name-only", since, "--"]
    else:
        # デフォルト: ステージ済み + 未コミット (working tree)
        cmd = ["git", "diff", "--name-only", "HEAD", "--"]

    try:
        result = _sp.run(cmd, cwd=str(root), capture_output=True, text=True, timeout=10)
        changed = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    except (FileNotFoundError, _sp.TimeoutExpired):
        print("⚠️ git が利用できません", file=sys.stderr)
        return 1

    if not changed:
        print("✅ 変更ファイルなし — guard pass")
        return 0

    # 2. .py と PROOF.md をフィルタ
    py_files = [Path(f) for f in changed if f.endswith(".py")]
    proof_files = [Path(f) for f in changed if f.endswith("PROOF.md")]

    if not py_files and not proof_files:
        print(f"✅ PROOF 関連の変更なし ({len(changed)} files changed) — guard pass")
        return 0

    # 3. 変更ファイルのみチェック
    checker = DendronChecker(check_dirs=True, check_files=True, check_functions=True)
    issues = []
    checked = 0

    for py in py_files:
        full = root / py
        if not full.exists():
            continue
        # ファイルの PURPOSE/REASON チェック
        file_proofs = checker.check_file_proof(full)
        if file_proofs and file_proofs.status == ProofStatus.MISSING:
            issues.append(f"  ❌ {py} — PROOF コメントなし")
        # 関数チェック
        func_proofs = checker.check_functions_in_file(full)
        for fp in func_proofs:
            if fp.status == ProofStatus.MISSING and not fp.is_private:
                issues.append(f"  ❌ {py}:{fp.line_number} {fp.name} — PURPOSE なし")
            elif fp.status == ProofStatus.WEAK:
                issues.append(f"  ⚠️ {py}:{fp.line_number} {fp.name} — {fp.quality_issue}")
        checked += 1

    for pf in proof_files:
        full = root / pf
        if not full.exists():
            continue
        dir_path = full.parent
        dir_proof = checker.check_dir_proof(dir_path)
        if dir_proof.status == ProofStatus.MISSING:
            issues.append(f"  ❌ {pf} — PURPOSE 未定義")
        elif dir_proof.status == ProofStatus.WEAK:
            issues.append(f"  ⚠️ {pf} — {dir_proof.reason}")
        checked += 1

    # 4. レポート出力
    print(f"🔍 Dendron Guard — {checked} files checked ({len(py_files)} .py, {len(proof_files)} PROOF.md)")

    if issues:
        print()
        for iss in issues:
            print(iss)
        print(f"\n❌ {len(issues)} issues found")
        return 1
    else:
        print("✅ Guard pass — all changed files OK")
        return 0


if __name__ == "__main__":
    sys.exit(main())
