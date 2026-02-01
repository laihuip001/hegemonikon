#!/usr/bin/env python3
# PROOF: [L2/インフラ] A0→継続する私が必要→boot_integration が担う
"""
Boot Integration - 3軸を統合した /boot 用 API

Usage:
    python boot_integration.py                    # 標準起動
    python boot_integration.py --mode fast        # 高速起動
    python boot_integration.py --mode detailed    # 詳細起動
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def get_boot_context(mode: str = "standard", context: Optional[str] = None) -> dict:
    """
    /boot 統合 API: 3軸（Handoff, Sophia, Persona）を統合して返す

    Args:
        mode: "fast" (/boot-), "standard" (/boot), "detailed" (/boot+)
        context: 現在のコンテキスト（Handoff の主題など）

    Returns:
        dict: {
            "handoffs": {...},    # 軸 A
            "ki": {...},          # 軸 B
            "persona": {...},     # 軸 C
            "formatted": str      # フォーマット済み出力
        }
    """
    # 軸 A: Handoff 活用
    from mekhane.symploke.handoff_search import get_boot_handoffs, format_boot_output

    handoffs_result = get_boot_handoffs(mode=mode, context=context)

    # 軸 B: Sophia アクティベーション
    # コンテキストを Handoff から取得
    ki_context = context
    if not ki_context and handoffs_result["latest"]:
        ki_context = handoffs_result["latest"].metadata.get("primary_task", "")
        if not ki_context:
            ki_context = handoffs_result["latest"].content[:200]

    from mekhane.symploke.sophia_ingest import get_boot_ki, format_ki_output

    ki_result = get_boot_ki(context=ki_context, mode=mode)

    # 軸 C: 人格永続化
    from mekhane.symploke.persona import get_boot_persona

    persona_result = get_boot_persona(mode=mode)

    # 統合フォーマット
    lines = []

    # Persona (最初に)
    if persona_result.get("formatted"):
        lines.append(persona_result["formatted"])
        lines.append("")

    # Handoff
    if handoffs_result["latest"]:
        lines.append(format_boot_output(handoffs_result, verbose=(mode == "detailed")))
        lines.append("")

    # KI
    if ki_result["ki_items"]:
        lines.append(format_ki_output(ki_result))

    return {
        "handoffs": handoffs_result,
        "ki": ki_result,
        "persona": persona_result,
        "formatted": "\n".join(lines),
    }


def print_boot_summary(mode: str = "standard", context: Optional[str] = None):
    """Print formatted boot summary."""
    result = get_boot_context(mode=mode, context=context)
    print(result["formatted"])

    # Summary line
    print()
    print("─" * 50)
    h_count = result["handoffs"]["count"]
    ki_count = result["ki"]["count"]
    sessions = result["persona"].get("sessions", 0)
    print(f"📊 Handoff: {h_count}件 | KI: {ki_count}件 | Sessions: {sessions}")


def main():
    parser = argparse.ArgumentParser(description="Boot integration API")
    parser.add_argument(
        "--mode", choices=["fast", "standard", "detailed"], default="standard", help="Boot mode"
    )
    parser.add_argument("--context", type=str, help="Context for search")
    args = parser.parse_args()

    import warnings

    warnings.filterwarnings("ignore")

    print_boot_summary(mode=args.mode, context=args.context)


if __name__ == "__main__":
    main()
