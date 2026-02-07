#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/symploke/ A0→継続する私が必要→boot_integration が担う
"""
Boot Integration - 6軸を統合した /boot 用 API

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
            "pks": {...},         # 軸 D
            "safety": {...},      # 軸 E
            "attractor": {...},   # 軸 F
            "formatted": str      # フォーマット済み出力
        }
    """
    # 軸 A: Handoff 活用
    print(" [1/6] 📋 Searching Handoffs...", file=sys.stderr, end="", flush=True)
    from mekhane.symploke.handoff_search import get_boot_handoffs, format_boot_output

    handoffs_result = get_boot_handoffs(mode=mode, context=context)
    print(" Done.", file=sys.stderr)

    # 軸 B: Sophia アクティベーション (タイムアウト付き)
    print(" [2/6] 📚 Ingesting Knowledge (Sophia)...", file=sys.stderr, end="", flush=True)
    # コンテキストを Handoff から取得
    ki_context = context
    if not ki_context and handoffs_result["latest"]:
        ki_context = handoffs_result["latest"].metadata.get("primary_task", "")
        if not ki_context:
            ki_context = handoffs_result["latest"].content[:200]

    ki_result = {"ki_items": [], "count": 0}
    try:
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

        def _run_sophia():
            from mekhane.symploke.sophia_ingest import get_boot_ki, format_ki_output
            return get_boot_ki(context=ki_context, mode=mode)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_sophia)
            ki_result = future.result(timeout=15.0)
        print(" Done.", file=sys.stderr)
    except (FutureTimeout, TimeoutError):
        print(" Timeout (skipped).", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({str(e)}).", file=sys.stderr)
    print(" [3/6] 👤 Loading Persona...", file=sys.stderr, end="", flush=True)
    from mekhane.symploke.persona import get_boot_persona

    persona_result = get_boot_persona(mode=mode)
    print(" Done.", file=sys.stderr)

    # 軸 D: PKS (能動的知識プッシュ)
    # 重い処理なのでタイムアウトを設定
    pks_result = {"nuggets": [], "count": 0, "formatted": ""}
    
    if mode != "fast":  # fastモードではPKSをスキップ
        print(" [4/6] 🧠 Activating PKS Engine...", file=sys.stderr, end="", flush=True)
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
         print(" [4/6] 🧠 PKS Engine skipped (fast mode).", file=sys.stderr)

    # 軸 E: Safety Contract Audit (v3.1)
    safety_result = {"skills": 0, "workflows": 0, "errors": 0, "warnings": 0, "formatted": ""}
    print(" [5/6] 🛡️ Running Safety Contract Audit...", file=sys.stderr, end="", flush=True)
    try:
        from mekhane.dendron.skill_checker import run_audit, AuditResult
        agent_dir = Path(__file__).parent.parent.parent / ".agent"
        if agent_dir.exists():
            audit = run_audit(agent_dir)
            dist = audit.risk_distribution()
            lcm = audit.lcm_distribution()
            safety_lines = []
            safety_lines.append("🛡️ **Safety Contract**")
            safety_lines.append(f"  Skills: {audit.skills_checked} | WF: {audit.workflows_checked}")
            risk_parts = [f"{k}:{v}" for k, v in dist.items() if v > 0]
            if risk_parts:
                safety_lines.append(f"  Risk: {' '.join(risk_parts)}")
            lcm_parts = [f"{k}:{v}" for k, v in lcm.items() if v > 0]
            if lcm_parts:
                safety_lines.append(f"  LCM:  {' '.join(lcm_parts)}")
            if audit.errors > 0:
                safety_lines.append(f"  ⚠️ {audit.errors} error(s), {audit.warnings} warning(s)")
            safety_result = {
                "skills": audit.skills_checked,
                "workflows": audit.workflows_checked,
                "errors": audit.errors,
                "warnings": audit.warnings,
                "formatted": "\n".join(safety_lines),
            }
        print(" Done.", file=sys.stderr)
    except Exception as e:
        print(f" Failed ({str(e)}).", file=sys.stderr)

    # 軸 F: Attractor Dispatch Engine
    attractor_result = {"series": [], "workflows": [], "llm_format": "", "formatted": ""}
    if context:
        print(" [6/6] 🎯 Attractor Dispatch...", file=sys.stderr, end="", flush=True)
        try:
            from concurrent.futures import ThreadPoolExecutor

            def _run_attractor():
                from mekhane.fep.attractor_advisor import AttractorAdvisor
                advisor = AttractorAdvisor(force_cpu=False)
                rec = advisor.recommend(context)
                llm_fmt = advisor.format_for_llm(context)
                return {
                    "series": rec.series,
                    "workflows": rec.workflows,
                    "llm_format": llm_fmt,
                    "confidence": rec.confidence,
                    "oscillation": rec.oscillation.value,
                    "advice": rec.advice,
                    "formatted": f"🎯 **Attractor**: {llm_fmt}" if llm_fmt else "",
                }

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_run_attractor)
                attractor_result = future.result(timeout=30.0)
            print(" Done.", file=sys.stderr)
        except TimeoutError:
            print(" Timeout (skipped).", file=sys.stderr)
        except Exception as e:
            print(f" Failed ({str(e)}).", file=sys.stderr)
    else:
        print(" [6/6] 🎯 Attractor skipped (no context).", file=sys.stderr)

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
        from mekhane.symploke.sophia_ingest import format_ki_output
        lines.append(format_ki_output(ki_result))

    # PKS
    if pks_result["formatted"]:
        lines.append("")
        lines.append(pks_result["formatted"])

    # Safety Contract
    if safety_result["formatted"]:
        lines.append("")
        lines.append(safety_result["formatted"])

    # Attractor
    if attractor_result["formatted"]:
        lines.append("")
        lines.append(attractor_result["formatted"])

    return {
        "handoffs": handoffs_result,
        "ki": ki_result,
        "persona": persona_result,
        "pks": pks_result,
        "safety": safety_result,
        "attractor": attractor_result,
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
    safety_errors = result.get("safety", {}).get("errors", 0)
    attractor_series = result.get("attractor", {}).get("series", [])
    attractor_str = "+".join(attractor_series) if attractor_series else "—"
    print(f"📊 Handoff: {h_count}件 | KI: {ki_count}件 | Sessions: {sessions} | PKS: {pks_count}件 | Safety: {'✅' if safety_errors == 0 else f'⚠️{safety_errors}'} | Attractor: {attractor_str}")


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
