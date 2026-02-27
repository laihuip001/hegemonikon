#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/ochema/claude_cli.py S2→Mekhane→Ochema
# PROOF: [L2/ツール] <- mekhane/ochema/ V15 headless LS Claude wrapper
# PURPOSE: IDE GUI なしで LS 経由 Claude を叩く CLI
# REASON: IDE を開かずにターミナルから Claude / Gemini 等を直接利用する
"""claude-cli — Headless Claude/Gemini CLI via Language Server.

IDE の GUI を起動せずに、バックグラウンドの Language Server プロセス経由で
Claude Sonnet 4.5 Thinking 等の LLM を直接叩けるコマンドラインツール。

前提条件:
    - Antigravity IDE が起動済み (LS プロセスが動いている)
    - または LS プロセスが何らかの方法でバックグラウンドで動作中

Usage:
    # 対話モード (REPL)
    python claude_cli.py

    # ワンショット
    python claude_cli.py -m "2+2は何?"

    # モデル指定
    python claude_cli.py -m "Hello" --model gemini-pro

    # パイプ入力
    echo "Explain FEP" | python claude_cli.py

    # Quota 確認
    python claude_cli.py --quota

    # モデル一覧
    python claude_cli.py --models

WARNING: ToS グレーゾーン。実験用途限定。公開禁止。
"""

from __future__ import annotations

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mekhane.ochema.antigravity_client import AntigravityClient, LLMResponse
from mekhane.ochema.proto import MODEL_ALIASES, DEFAULT_MODEL, resolve_model


# --- ANSI Colors ---

class C:
    """ANSI color codes."""
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    RESET = "\033[0m"


# --- Display Helpers ---

def print_response(resp: LLMResponse) -> None:
    """LLM 応答を整形出力する。"""
    # Thinking (折りたたみ)
    if resp.thinking:
        print(f"\n{C.DIM}── thinking ──{C.RESET}")
        # 長い thinking は先頭 500 文字のみ
        thinking = resp.thinking
        if len(thinking) > 500:
            thinking = thinking[:500] + f"\n{C.DIM}... ({len(resp.thinking)} chars total){C.RESET}"
        print(f"{C.DIM}{thinking}{C.RESET}")
        print(f"{C.DIM}── /thinking ──{C.RESET}\n")

    # Response
    print(f"{C.GREEN}{resp.text}{C.RESET}")

    # Metadata
    model_display = resp.model.replace("MODEL_", "").replace("_", " ").title()
    print(f"\n{C.DIM}[{model_display}]{C.RESET}")


def print_quota(client: AntigravityClient) -> None:
    """Quota 情報を整形出力する。"""
    try:
        quota = client.quota_status()
    except Exception as e:
        print(f"{C.RED}Error: {e}{C.RESET}")
        return

    print(f"\n{C.BOLD}📊 Model Quota{C.RESET}\n")
    for m in quota.get("models", []):
        pct = m["remaining_pct"]
        if pct >= 50:
            color = C.GREEN
        elif pct >= 20:
            color = C.YELLOW
        else:
            color = C.RED
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        rec = " ⭐" if m.get("recommended") else ""
        print(f"  {m['label']:40s} {color}{bar} {pct:3d}%{C.RESET}{rec}")

    print(f"\n{C.DIM}Total: {quota.get('total_models', 0)} models{C.RESET}")


def print_models() -> None:
    """利用可能なモデルエイリアスを表示。"""
    print(f"\n{C.BOLD}🤖 Available Models{C.RESET}\n")
    print(f"  {'Alias':20s} {'Proto Enum':45s}")
    print(f"  {'─' * 20} {'─' * 45}")
    for alias, enum in MODEL_ALIASES.items():
        default = " (default)" if enum == DEFAULT_MODEL else ""
        print(f"  {alias:20s} {enum:45s}{C.DIM}{default}{C.RESET}")
    print(f"\n{C.DIM}Use --model <alias> or --model MODEL_xxx{C.RESET}")


def repl(client: AntigravityClient, model: str, timeout: float) -> None:
    """対話モード (REPL)。"""
    model_short = model.replace("MODEL_", "").replace("_", " ").title()
    print(f"\n{C.BOLD}{C.CYAN}╔══════════════════════════════════════╗{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}║  claude-cli — Headless LLM Terminal  ║{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}╚══════════════════════════════════════╝{C.RESET}")
    print(f"{C.DIM}Model: {model_short} | Timeout: {timeout}s{C.RESET}")
    print(f"{C.DIM}Commands: /quit /model <name> /quota /models /clear{C.RESET}")
    print()

    while True:
        try:
            prompt = input(f"{C.BOLD}{C.CYAN}> {C.RESET}")
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.DIM}Bye.{C.RESET}")
            break

        prompt = prompt.strip()
        if not prompt:
            continue

        # Slash commands
        if prompt == "/quit" or prompt == "/q":
            print(f"{C.DIM}Bye.{C.RESET}")
            break
        elif prompt == "/quota":
            print_quota(client)
            continue
        elif prompt == "/models":
            print_models()
            continue
        elif prompt == "/clear":
            os.system("clear")
            continue
        elif prompt.startswith("/model "):
            new_model = prompt[7:].strip()
            model = resolve_model(new_model)
            model_short = model.replace("MODEL_", "").replace("_", " ").title()
            print(f"{C.DIM}Model → {model_short}{C.RESET}")
            continue

        # Send to LLM
        try:
            print(f"{C.DIM}⏳ Thinking...{C.RESET}", end="", flush=True)
            resp = client.ask(prompt, model=model, timeout=timeout)
            # Clear the "Thinking..." line
            print(f"\r{' ' * 40}\r", end="")
            print_response(resp)
        except Exception as e:
            print(f"\r{C.RED}Error: {e}{C.RESET}")

        print()


# --- Main ---

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Headless Claude/Gemini CLI via Language Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # 対話モード
  %(prog)s -m "2+2は何?"            # ワンショット
  %(prog)s -m "Hello" --model gemini-pro
  %(prog)s --quota                  # Quota 確認
  %(prog)s --models                 # モデル一覧
  echo "Explain X" | %(prog)s       # パイプ入力
""",
    )
    parser.add_argument("-m", "--message", help="Send a single message (non-interactive)")
    parser.add_argument("--model", default="claude-sonnet",
                        help=f"Model name or alias (default: claude-sonnet)")
    parser.add_argument("--timeout", type=float, default=120,
                        help="Max wait seconds (default: 120)")
    parser.add_argument("--quota", action="store_true",
                        help="Show quota info and exit")
    parser.add_argument("--models", action="store_true",
                        help="Show available models and exit")
    parser.add_argument("--thinking", action="store_true",
                        help="Show full thinking output (no truncation)")
    parser.add_argument("--raw", action="store_true",
                        help="Raw output only (no colors, no metadata)")

    args = parser.parse_args()
    model = resolve_model(args.model)

    # Connect to LS
    try:
        client = AntigravityClient()
        ls = client.ls
        if not args.raw:
            print(f"{C.DIM}Connected to LS (PID:{ls.pid}, PORT:{ls.port}){C.RESET}",
                  file=sys.stderr)
    except Exception as e:
        print(f"{C.RED}Error: Cannot connect to Language Server: {e}{C.RESET}",
              file=sys.stderr)
        print(f"{C.DIM}Is Antigravity IDE running?{C.RESET}", file=sys.stderr)
        sys.exit(1)

    # Dispatch
    if args.models:
        print_models()
        return

    if args.quota:
        print_quota(client)
        return

    # Pipe input
    if not sys.stdin.isatty() and not args.message:
        args.message = sys.stdin.read().strip()

    if args.message:
        # One-shot mode
        try:
            resp = client.ask(args.message, model=model, timeout=args.timeout)
            if args.raw:
                print(resp.text)
            else:
                print_response(resp)
        except Exception as e:
            print(f"{C.RED}Error: {e}{C.RESET}", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive REPL
        repl(client, model, args.timeout)


if __name__ == "__main__":
    main()
