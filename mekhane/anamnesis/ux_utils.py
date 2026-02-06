# PROOF: [L2/インフラ] <- mekhane/anamnesis/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

P3 → ユーザー体験の向上が必要
   → CLI出力の視認性と統一性が必要
   → ux_utils.py が担う

Q.E.D.

---

UX Utilities - ユーザー体験ユーティリティ

標準化された色分けとセマンティックな出力機能を提供します。
"""

import sys
from typing import Optional, List

try:
    from termcolor import colored, cprint
except ImportError:
    # Fallback if termcolor is not installed
    def colored(
        text: str,
        color: Optional[str] = None,
        on_color: Optional[str] = None,
        attrs: Optional[List[str]] = None,
    ) -> str:
        return text

    def cprint(
        text: str,
        color: Optional[str] = None,
        on_color: Optional[str] = None,
        attrs: Optional[List[str]] = None,
        **kwargs,
    ) -> None:
        print(text, **kwargs)


def print_success(message: str) -> None:
    """成功メッセージを緑色で表示"""
    cprint(f"✔ {message}", "green")


def print_error(message: str) -> None:
    """エラーメッセージを赤色で表示"""
    cprint(f"✖ {message}", "red", attrs=["bold"])


def print_warning(message: str) -> None:
    """警告メッセージを黄色で表示"""
    cprint(f"⚠ {message}", "yellow")


def print_info(message: str) -> None:
    """情報メッセージをシアン色で表示"""
    cprint(f"ℹ {message}", "cyan")


def print_header(message: str) -> None:
    """ヘッダーをマゼンタ色の太字で表示"""
    cprint(f"\n{message}", "magenta", attrs=["bold"])
    cprint("=" * len(message), "magenta")


def colorize_usage(token_current: int, token_limit: int) -> str:
    """トークン使用率に応じて色付けした文字列を返す"""
    if token_limit == 0:
        return f"{token_current:,} / 0"

    percentage = (token_current / token_limit) * 100
    text = f"{token_current:,} / {token_limit:,} ({percentage:.1f}%)"

    if percentage > 90:
        return colored(text, "red", attrs=["bold"])
    elif percentage > 75:
        return colored(text, "yellow")
    else:
        return colored(text, "green")
