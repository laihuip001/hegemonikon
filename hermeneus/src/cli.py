# PROOF: [L2/インフラ] Hermēneus CLI
"""
Hermēneus CLI — コマンドラインインターフェース

CCL のコンパイル、実行、検証をコマンドラインから実行。

Usage:
    hermeneus compile "/noe+ >> V[] < 0.3"
    hermeneus execute "/noe+" --context "分析対象"
    hermeneus verify "/ene+"
    hermeneus audit --period 7

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

try:
    from termcolor import colored, cprint
except ImportError:
    # Fallback if termcolor is not installed
    def colored(text, color=None, on_color=None, attrs=None):
        return text

    def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
        print(text, **kwargs)


class UX:
    """CLI UX Helper"""

    @staticmethod
    def print_header(text: str):
        cprint(f"\n=== {text} ===", "cyan", attrs=["bold"])

    @staticmethod
    def print_success(text: str):
        cprint(f"✅ {text}", "green", attrs=["bold"])

    @staticmethod
    def print_error(text: str):
        cprint(f"❌ {text}", "red", attrs=["bold"], file=sys.stderr)

    @staticmethod
    def print_warning(text: str):
        cprint(f"⚠️ {text}", "yellow", attrs=["bold"])

    @staticmethod
    def print_info(text: str):
        cprint(f"ℹ️ {text}", "blue")

    @staticmethod
    def print_kv(key: str, value: str, color: str = "white"):
        """Print Key-Value pair"""
        print(f"{colored(key + ':', 'cyan')} {colored(value, color)}")


def create_parser() -> argparse.ArgumentParser:
    """CLI パーサーを作成"""
    parser = argparse.ArgumentParser(
        prog="hermeneus",
        description="Hermēneus — CCL 実行保証コンパイラ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hermeneus compile "/noe+ >> V[] < 0.3"
  hermeneus execute "/noe+" --context "プロジェクト分析"
  hermeneus verify "/ene+" --rounds 3
  hermeneus audit --period 7
"""
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 0.4.1"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="コマンド")
    
    # compile サブコマンド
    compile_parser = subparsers.add_parser(
        "compile",
        help="CCL を LMQL にコンパイル"
    )
    compile_parser.add_argument("ccl", help="CCL 式")
    compile_parser.add_argument(
        "--model", "-m",
        default="openai/gpt-4o",
        help="モデル (デフォルト: openai/gpt-4o)"
    )
    compile_parser.add_argument(
        "--output", "-o",
        help="出力ファイル"
    )
    
    # execute サブコマンド
    execute_parser = subparsers.add_parser(
        "execute",
        help="CCL を実行"
    )
    execute_parser.add_argument("ccl", help="CCL 式")
    execute_parser.add_argument(
        "--context", "-c",
        default="",
        help="コンテキスト"
    )
    execute_parser.add_argument(
        "--model", "-m",
        default="openai/gpt-4o",
        help="モデル"
    )
    execute_parser.add_argument(
        "--output", "-o",
        help="出力ファイル"
    )
    execute_parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 形式で出力"
    )
    
    # verify サブコマンド
    verify_parser = subparsers.add_parser(
        "verify",
        help="CCL 実行結果を検証 (Multi-Agent Debate)"
    )
    verify_parser.add_argument("ccl", help="CCL 式")
    verify_parser.add_argument(
        "--context", "-c",
        default="",
        help="コンテキスト"
    )
    verify_parser.add_argument(
        "--rounds", "-r",
        type=int,
        default=3,
        help="ディベートラウンド数 (デフォルト: 3)"
    )
    verify_parser.add_argument(
        "--min-conf",
        type=float,
        default=0.7,
        help="最低確信度 (デフォルト: 0.7)"
    )
    verify_parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 形式で出力"
    )
    
    # audit サブコマンド
    audit_parser = subparsers.add_parser(
        "audit",
        help="監査レポートを表示"
    )
    audit_parser.add_argument(
        "--period", "-p",
        default="last_7_days",
        help="期間 (today, last_24h, last_7_days, last_30_days, all)"
    )
    audit_parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="出力形式"
    )
    audit_parser.add_argument(
        "--limit", "-l",
        type=int,
        default=10,
        help="表示件数"
    )
    
    # type-check サブコマンド
    typecheck_parser = subparsers.add_parser(
        "typecheck",
        help="Python コードの型チェック"
    )
    typecheck_parser.add_argument(
        "file",
        help="Python ファイルパス"
    )
    typecheck_parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict モード"
    )
    
    return parser


def cmd_compile(args) -> int:
    """compile コマンド"""
    from . import compile_ccl
    
    try:
        # UX.print_header(f"Compiling: {args.ccl}")
        lmql_code = compile_ccl(args.ccl, model=args.model)
        
        if args.output:
            Path(args.output).write_text(lmql_code)
            UX.print_success(f"Compiled to: {args.output}")
        else:
            print(lmql_code)
        
        return 0
    except Exception as e:
        UX.print_error(str(e))
        return 1


def cmd_execute(args) -> int:
    """execute コマンド"""
    from . import execute_ccl
    
    try:
        if not args.json:
            UX.print_header("Executing CCL Workflow")
            UX.print_kv("CCL", args.ccl)
            if args.context:
                UX.print_kv("Context", args.context)
            UX.print_info("Processing...")

        result = execute_ccl(
            args.ccl,
            context=args.context,
            model=args.model
        )
        
        if args.json:
            output = {
                "status": result.status.value,
                "output": result.output,
                "metadata": result.metadata
            }
            output_str = json.dumps(output, ensure_ascii=False, indent=2)
            print(output_str)
            content_to_save = output_str
        else:
            if result.status.value == "success":
                UX.print_success("Execution Successful")
            else:
                UX.print_error(f"Execution Failed: {result.status.value}")

            print("\n" + result.output)
            content_to_save = result.output
        
        if args.output:
            Path(args.output).write_text(content_to_save)
            UX.print_info(f"Output saved to: {args.output}")
        
        return 0 if result.status.value == "success" else 1
    except Exception as e:
        UX.print_error(str(e))
        return 1


def cmd_verify(args) -> int:
    """verify コマンド"""
    from . import execute_ccl, verify_execution, record_verification
    
    try:
        if not args.json:
            UX.print_header("Verifying Execution")
            UX.print_kv("CCL", args.ccl)
            UX.print_info("Executing and Debating...")

        # まず実行
        exec_result = execute_ccl(args.ccl, context=args.context)
        
        # 検証
        consensus = verify_execution(
            args.ccl,
            exec_result.output,
            context=args.context,
            debate_rounds=args.rounds,
            min_confidence=args.min_conf
        )
        
        # 監査記録
        record_verification(args.ccl, exec_result.output, consensus)
        
        if args.json:
            output = {
                "accepted": consensus.accepted,
                "confidence": consensus.confidence,
                "majority_ratio": consensus.majority_ratio,
                "dissent_reasons": consensus.dissent_reasons,
                "verdict": {
                    "type": consensus.verdict.type.value,
                    "reasoning": consensus.verdict.reasoning
                }
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            if consensus.accepted:
                UX.print_success("ACCEPTED")
            else:
                UX.print_error("REJECTED")

            conf_color = "green" if consensus.confidence > 0.8 else "yellow" if consensus.confidence > 0.5 else "red"
            UX.print_kv("Confidence", f"{consensus.confidence:.1%}", color=conf_color)
            UX.print_kv("Majority", f"{consensus.majority_ratio:.1%}")

            if consensus.dissent_reasons:
                UX.print_warning("Dissent Reasons:")
                for reason in consensus.dissent_reasons:
                    print(colored(f"  - {reason}", "yellow"))
        
        return 0 if consensus.accepted else 1
    except Exception as e:
        UX.print_error(str(e))
        return 1


def cmd_audit(args) -> int:
    """audit コマンド"""
    from . import query_audits, get_audit_report
    
    try:
        if args.format == "json":
            records = query_audits(period=args.period, limit=args.limit)
            output = [
                {
                    "record_id": r.record_id,
                    "ccl": r.ccl_expression,
                    "accepted": r.consensus_accepted,
                    "confidence": r.confidence,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in records
            ]
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            report = get_audit_report(period=args.period)
            # Assuming report is already formatted string
            print(report)
        
        return 0
    except Exception as e:
        UX.print_error(str(e))
        return 1


def cmd_typecheck(args) -> int:
    """typecheck コマンド"""
    from . import verify_code, MypyProver
    
    try:
        path = Path(args.file)
        if not path.exists():
            UX.print_error(f"File not found: {args.file}")
            return 1
        
        code = path.read_text()
        prover = MypyProver(strict=args.strict)
        
        if not prover.is_available():
            UX.print_error("mypy is not available")
            return 1
        
        UX.print_info(f"Checking {args.file}...")
        result = prover.verify(code)
        
        if result.verified:
            UX.print_success(f"Type check passed ({result.execution_time_ms:.0f}ms)")
            return 0
        else:
            UX.print_error("Type check failed")
            for error in result.errors:
                print(colored(f"  - {error}", "red"))
            return 1
    except Exception as e:
        UX.print_error(str(e))
        return 1


def main(argv: Optional[list] = None) -> int:
    """CLI メイン"""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    commands = {
        "compile": cmd_compile,
        "execute": cmd_execute,
        "verify": cmd_verify,
        "audit": cmd_audit,
        "typecheck": cmd_typecheck,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
