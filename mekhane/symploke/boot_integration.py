#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→継続する私が必要→boot_integration が担う
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
    print(" [1/4] 📋 Searching Handoffs...", file=sys.stderr, end="", flush=True)
    from mekhane.symploke.handoff_search import get_boot_handoffs, format_boot_output

    handoffs_result = get_boot_handoffs(mode=mode, context=context)
    print(" Done.", file=sys.stderr)

    # 軸 B: Sophia アクティベーション
    print(" [2/4] 📚 Ingesting Knowledge (Sophia)...", file=sys.stderr, end="", flush=True)
    # コンテキストを Handoff から取得
    ki_context = context
    if not ki_context and handoffs_result["latest"]:
        ki_context = handoffs_result["latest"].metadata.get("primary_task", "")
        if not ki_context:
            ki_context = handoffs_result["latest"].content[:200]

    from mekhane.symploke.sophia_ingest import get_boot_ki, format_ki_output

    ki_result = get_boot_ki(context=ki_context, mode=mode)
    print(" Done.", file=sys.stderr)

    # 軸 C: 人格永続化
    print(" [4/4] 👤 Loading Persona...", file=sys.stderr, end="", flush=True)
    from mekhane.symploke.persona import get_boot_persona

    persona_result = get_boot_persona(mode=mode)
    print(" Done.", file=sys.stderr)

    # 軸 D: PKS (能動的知識プッシュ)
    # 重い処理なのでタイムアウトを設定
    pks_result = {"nuggets": [], "count": 0, "formatted": ""}
    
    if mode != "fast":  # fastモードではPKSをスキップ
        print(" [3/4] 🧠 Activating PKS Engine...", file=sys.stderr, end="", flush=True)
        try:
            from concurrent.futures import ThreadPoolExecutor
            
            def _run_pks():
                from mekhane.pks.pks_engine import PKSEngine
                pks_engine = PKSEngine(threshold=0.5, max_push=3)
                
                # コンテキスト設定
                pks_topics = []
                if context:
                    pks_topics = [t.strip() for t in context.split(",")]
                elif ki_context:
                    # KI コンテキストからトピック抽出
                    words = ki_context.split()[:5]
                    pks_topics = [w for w in words if len(w) > 2]
                
                if pks_topics:
                    pks_engine.set_context(topics=pks_topics)
                    return pks_engine.proactive_push(k=10)
                return []

            # 10秒タイムアウト (detailedでも待たせすぎない)
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_run_pks)
                nuggets = future.result(timeout=10.0)
                
            if nuggets:
                from mekhane.pks.pks_engine import PKSEngine  # 型ヒント用
                # インスタンス化せずにフォーマットメソッドだけ借用したいが、インスタンスメソッドなので
                # 簡易フォーマッターを使用するか、再インスタンス化する（軽量）
                pks_engine_dummy = PKSEngine()
                pks_result = {
                    "nuggets": nuggets,
                    "count": len(nuggets),
                    "formatted": pks_engine_dummy.format_push_report(nuggets),
                }
            print(" Done.", file=sys.stderr)
            
        except TimeoutError:
            print(" Timeout (skipped).", file=sys.stderr)
        except Exception as e:
            print(f" Failed ({str(e)}).", file=sys.stderr)
    else:
         print(" [3/4] 🧠 PKS Engine skipped (fast mode).", file=sys.stderr)

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

    # PKS
    if pks_result["formatted"]:
        lines.append("")
        lines.append(pks_result["formatted"])

    return {
        "handoffs": handoffs_result,
        "ki": ki_result,
        "persona": persona_result,
        "pks": pks_result,
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
    pks_count = result.get("pks", {}).get("count", 0)
    print(f"📊 Handoff: {h_count}件 | KI: {ki_count}件 | Sessions: {sessions} | PKS: {pks_count}件")


def main():
    parser = argparse.ArgumentParser(description="Boot integration API")
    parser.add_argument(
        "--mode",
        choices=["fast", "standard", "detailed"],
        default="standard",
        help="Boot mode",
    )
    parser.add_argument("--context", type=str, help="Context for search")
    args = parser.parse_args()

    import warnings

    warnings.filterwarnings("ignore")

    print(f"⏳ Boot Mode: {args.mode}", file=sys.stderr)
    
    try:
        print_boot_summary(mode=args.mode, context=args.context)
    except KeyboardInterrupt:
        print("\n⚠️ Boot sequence interrupted.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Boot sequence failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
