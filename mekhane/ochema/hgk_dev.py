#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- ochema/ A0→Implementation→hgk_dev
# PROOF: [L2/インフラ] <- mekhane/ochema/ A0→Cortex ヘッドレス HGK 開発 CLI
# PURPOSE: IDE なしで Cortex API 経由の HGK 開発を可能にする対話型 CLI

"""
hgk-dev — Cortex API ヘッドレス HGK 開発 CLI

IDE (Antigravity) を起動せずに、Cortex API 経由で AI と対話しながら
HGK 開発を行うための CLI ツール。

Architecture:
    User (terminal) → hgk-dev CLI → CortexClient
        → Gemini: ask_with_tools() (generateContent + Function Calling)
        → Claude: chat() (generateChat) + text-based tool use
    Both routes support local file read/write/search/command execution.

Available models (ALL free via AI Ultra):
    Gemini: gemini-3-pro-preview, gemini-2.5-pro, gemini-2.5-flash
    Claude: claude-sonnet-4-5, claude-opus-4-6

Usage:
    python -m mekhane.ochema.hgk_dev
    python -m mekhane.ochema.hgk_dev --model claude-sonnet-4-5
    python -m mekhane.ochema.hgk_dev --model gemini-3-pro-preview --budget 8192
"""

from __future__ import annotations

import argparse
import json
import os
import readline
import sys
import time
from pathlib import Path
from typing import Any

# --- Constants ---

HISTFILE = Path.home() / ".hgk_dev_history"
MAX_HISTORY = 500

# Claude models use generateChat + text-based tool use
CLAUDE_MODELS = {"claude-sonnet-4-5", "claude-opus-4-6"}

# Gemini models use generateContent + native Function Calling
GEMINI_MODELS = {
    "gemini-3-pro-preview", "gemini-3-flash-preview",
    "gemini-2.5-pro", "gemini-2.5-flash",
    "gemini-2.0-flash",
}

ALL_MODELS = CLAUDE_MODELS | GEMINI_MODELS

DEFAULT_MODEL = "gemini-3-pro-preview"

# --- Colors ---

class C:
    """ANSI color codes."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


# --- System Prompts ---

HGK_DEV_SYSTEM_PROMPT = """\
あなたは Hegemonikón 認知ハイパーバイザーフレームワークの開発アシスタントです。
ローカルファイルの読み書き、検索、コマンド実行が可能なツールを持っています。

## ワークスペース
- ~/oikos/hegemonikon — メインプロジェクト
- ~/oikos/mneme — 記憶・セッション管理

## プロジェクト構造
- kernel/: 公理体系 (SACRED — 変更禁止)
- mekhane/: 実装 (ochema, periskope, mcp, basanos, etc.)
- synergeia/: 統合レイヤー
- .agent/: ルール、スキル、ワークフロー

## ガイドライン
- ファイル変更前に必ず read_file で現状を確認する
- 破壊的操作前に計画を説明する
- 不確かな場合は [推定] [仮説] ラベルを付ける
- 全出力は日本語 (コードコメントは英語可)
- kernel/ のファイルを変更してはならない
- rm -rf, git push --force は実行禁止
- テスト: cd ~/oikos/hegemonikon && .venv/bin/python -m pytest
"""


def _is_claude(model: str) -> bool:
    """Check if model is a Claude model."""
    return model in CLAUDE_MODELS or model.startswith("claude")


# --- Gemini Agent (native Function Calling) ---

def _run_gemini_turn(
    client: Any,
    message: str,
    *,
    model: str,
    system_instruction: str,
    thinking_budget: int | None,
    max_iterations: int,
    max_tokens: int,
    timeout: float,
) -> str:
    """Run a single turn with Gemini's native tool use."""
    response = client.ask_with_tools(
        message=message,
        model=model,
        system_instruction=system_instruction,
        thinking_budget=thinking_budget,
        max_iterations=max_iterations,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    return response.text


# --- Claude Agent (text-based tool use via generateChat) ---

def _run_claude_turn(
    client: Any,
    message: str,
    history: list[dict[str, Any]],
    *,
    model: str,
    system_instruction: str,
    max_iterations: int,
    timeout: float,
) -> tuple[str, list[dict[str, Any]]]:
    """Run a single turn with Claude's text-based tool use.

    Returns:
        (final_text, updated_history)
    """
    from .tools import (
        build_tool_descriptions,
        execute_tool,
        has_tool_calls,
        parse_tool_calls_from_text,
        strip_tool_calls,
    )

    # Prepend tool instructions to the user message on first turn
    if not history:
        tool_desc = build_tool_descriptions()
        prefixed = (
            f"{system_instruction}\n\n"
            f"## ツール\n"
            f"ツールを使うときは以下のフォーマットで応答してください:\n\n"
            f"```tool_call\n"
            f'{{"name": "tool_name", "args": {{"arg1": "value1"}}}}\n'
            f"```\n\n"
            f"利用可能なツール:\n{tool_desc}\n\n"
            f"パスは /home/makaron8426/oikos/ 以下の絶対パスを使ってください。\n\n"
            f"---\n\n{message}"
        )
    else:
        prefixed = message

    # Add user message to history
    history.append({"author": 1, "content": prefixed})

    for iteration in range(max_iterations):
        response = client.chat(
            message=prefixed if iteration == 0 else "",
            model=model,
            history=history if iteration > 0 else history[:-1],
            timeout=timeout,
        )

        text = response.text

        if not has_tool_calls(text):
            # No tool calls — final response
            history.append({"author": 2, "content": text})
            return text, history

        # Execute tool calls
        tool_calls = parse_tool_calls_from_text(text)
        results: list[str] = []

        for tc in tool_calls:
            name = tc["name"]
            args = tc["args"]
            print(f"  {C.DIM}🔧 {name}({json.dumps(args, ensure_ascii=False)[:80]}){C.RESET}")
            result = execute_tool(name, args)
            results.append(f"## {name} result:\n```json\n{json.dumps(result, ensure_ascii=False, indent=2)[:2000]}\n```")

        # Add model response + tool results to history
        history.append({"author": 2, "content": text})
        tool_result_text = "\n\n".join(results)
        history.append({"author": 1, "content": f"ツール実行結果:\n\n{tool_result_text}\n\n続けてください。"})
        prefixed = ""  # Next iteration uses history only

    # Max iterations
    narrative = strip_tool_calls(text) if text else ""
    history.append({"author": 2, "content": narrative + "\n\n(最大ツール使用回数に達しました)"})
    return narrative + "\n\n(最大ツール使用回数に達しました)", history


# --- REPL ---

def _print_banner(model: str, thinking_budget: int | None) -> None:
    """Print startup banner."""
    model_type = "Claude (generateChat)" if _is_claude(model) else "Gemini (generateContent)"
    budget_str = f" | budget={thinking_budget}" if thinking_budget is not None else ""

    print(f"""
{C.CYAN}{C.BOLD}╔═══════════════════════════════════════════════╗
║        hgk-dev — ヘッドレス HGK 開発 CLI       ║
╚═══════════════════════════════════════════════╝{C.RESET}
  {C.GREEN}モデル{C.RESET}: {model} ({model_type}{budget_str})
  {C.GREEN}ツール{C.RESET}: read_file, write_file, search_text, run_command, git_diff, git_log
  {C.GREEN}コマンド{C.RESET}: /quit /model /clear /help
  {C.DIM}Cortex API 経由 — IDE 不要 — 全モデル無料 (AI Ultra){C.RESET}
""")


def _print_help() -> None:
    """Print help."""
    print(f"""
{C.BOLD}スラッシュコマンド:{C.RESET}
  /quit, /q       — 終了
  /model <name>   — モデル切替 (e.g. /model claude-sonnet-4-5)
  /models         — 利用可能モデル一覧
  /clear          — 会話履歴クリア
  /history        — 会話履歴表示
  /help, /h       — このヘルプ
""")


def main() -> None:
    """Main REPL entry point."""
    parser = argparse.ArgumentParser(
        description="hgk-dev — Cortex API ヘッドレス HGK 開発 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "例:\n"
            "  python -m mekhane.ochema.hgk_dev\n"
            "  python -m mekhane.ochema.hgk_dev --model claude-sonnet-4-5\n"
            "  python -m mekhane.ochema.hgk_dev --model gemini-2.5-pro --budget 8192\n"
        ),
    )
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL,
                       help=f"モデル (default: {DEFAULT_MODEL})")
    parser.add_argument("--budget", "-b", type=int, default=None,
                       help="Thinking budget (Gemini のみ)")
    parser.add_argument("--max-iterations", "-i", type=int, default=10,
                       help="最大ツール使用回数/ターン (default: 10)")
    parser.add_argument("--max-tokens", "-t", type=int, default=8192,
                       help="最大出力トークン (default: 8192)")
    parser.add_argument("--timeout", type=float, default=120.0,
                       help="API タイムアウト秒 (default: 120)")

    args = parser.parse_args()
    model = args.model
    thinking_budget = args.budget

    # Import client
    try:
        from .cortex_client import CortexClient
    except ImportError:
        # Direct execution
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from mekhane.ochema.cortex_client import CortexClient

    client = CortexClient()

    # Setup readline history
    try:
        readline.read_history_file(str(HISTFILE))
    except FileNotFoundError:
        pass
    readline.set_history_length(MAX_HISTORY)

    # State
    claude_history: list[dict[str, Any]] = []

    _print_banner(model, thinking_budget)

    try:
        while True:
            try:
                prompt = input(f"{C.BOLD}{C.BLUE}>>> {C.RESET}")
            except EOFError:
                print("\n")
                break

            prompt = prompt.strip()
            if not prompt:
                continue

            # --- Slash commands ---
            if prompt.startswith("/"):
                cmd_parts = prompt.split(maxsplit=1)
                cmd = cmd_parts[0].lower()

                if cmd in ("/quit", "/q"):
                    break
                elif cmd == "/model":
                    if len(cmd_parts) < 2:
                        print(f"  現在: {C.GREEN}{model}{C.RESET}")
                        continue
                    new_model = cmd_parts[1].strip()
                    if new_model not in ALL_MODELS:
                        print(f"  {C.RED}不明なモデル: {new_model}{C.RESET}")
                        print(f"  利用可能: {', '.join(sorted(ALL_MODELS))}")
                        continue
                    model = new_model
                    claude_history = []  # Reset history on model change
                    _print_banner(model, thinking_budget)
                elif cmd == "/models":
                    print(f"\n  {C.BOLD}Gemini (generateContent + Function Calling):{C.RESET}")
                    for m in sorted(GEMINI_MODELS):
                        marker = " ← 現在" if m == model else ""
                        print(f"    {C.GREEN}{m}{C.RESET}{marker}")
                    print(f"\n  {C.BOLD}Claude (generateChat + text-based tool use):{C.RESET}")
                    for m in sorted(CLAUDE_MODELS):
                        marker = " ← 現在" if m == model else ""
                        print(f"    {C.MAGENTA}{m}{C.RESET}{marker}")
                    print()
                elif cmd == "/clear":
                    claude_history = []
                    print(f"  {C.DIM}会話履歴をクリアしました{C.RESET}")
                elif cmd == "/history":
                    if _is_claude(model):
                        print(f"  Claude 履歴: {len(claude_history)} メッセージ")
                        for i, h in enumerate(claude_history[-6:]):
                            role = "User" if h["author"] == 1 else "AI"
                            print(f"    [{role}] {h['content'][:60]}...")
                    else:
                        print(f"  {C.DIM}Gemini はターンごとにリセットされます{C.RESET}")
                elif cmd in ("/help", "/h"):
                    _print_help()
                else:
                    print(f"  {C.RED}不明なコマンド: {cmd}{C.RESET} (/help で一覧)")
                continue

            # --- AI query ---
            start_time = time.monotonic()

            try:
                if _is_claude(model):
                    # Claude: generateChat + text-based tool use
                    text, claude_history = _run_claude_turn(
                        client, prompt, claude_history,
                        model=model,
                        system_instruction=HGK_DEV_SYSTEM_PROMPT,
                        max_iterations=args.max_iterations,
                        timeout=args.timeout,
                    )
                else:
                    # Gemini: generateContent + native Function Calling
                    text = _run_gemini_turn(
                        client, prompt,
                        model=model,
                        system_instruction=HGK_DEV_SYSTEM_PROMPT,
                        thinking_budget=thinking_budget,
                        max_iterations=args.max_iterations,
                        max_tokens=args.max_tokens,
                        timeout=args.timeout,
                    )

                elapsed = time.monotonic() - start_time
                print(f"\n{C.GREEN}{'─' * 60}{C.RESET}")
                print(text)
                print(f"{C.GREEN}{'─' * 60}{C.RESET}")
                print(f"  {C.DIM}{model} | {elapsed:.1f}s{C.RESET}\n")

            except KeyboardInterrupt:
                print(f"\n  {C.YELLOW}中断しました{C.RESET}")
            except Exception as e:
                print(f"\n  {C.RED}エラー: {e}{C.RESET}\n")

    finally:
        # Save readline history
        try:
            readline.write_history_file(str(HISTFILE))
        except OSError:
            pass
        print(f"\n{C.DIM}hgk-dev 終了{C.RESET}")


if __name__ == "__main__":
    main()
