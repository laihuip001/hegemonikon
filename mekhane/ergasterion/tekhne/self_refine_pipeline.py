#!/usr/bin/env python3
"""
Self-Refine Pipeline — プロンプトの品質を自動改善

2つのモード:
  1. 静的解析 (--mode static): prompt_quality_scorer による改善提案
  2. LLM Self-Refine (--mode llm): Hermēneus execute /dia- で批評→改善

Usage:
  # 静的解析のみ
  python self_refine_pipeline.py --input prompt.skill.md --mode static

  # LLM Self-Refine (Hermēneus 経由)
  python self_refine_pipeline.py --input prompt.skill.md --mode llm

  # 両方 (静的 → LLM)
  python self_refine_pipeline.py --input prompt.skill.md --mode full
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Import scorer
sys.path.insert(0, str(Path(__file__).parent))
from prompt_quality_scorer import QualityReport, format_report, score_prompt


def static_refine(filepath: str, threshold: int = 80, max_iter: int = 3) -> dict:
    """
    Run static analysis refinement loop.
    Returns suggestions without modifying the file.
    """
    report = score_prompt(filepath)
    iterations = []

    iterations.append({
        "iteration": 0,
        "score": report.total,
        "grade": report.grade,
        "status": "initial",
    })

    print(format_report(report, verbose=True))

    if report.total >= threshold:
        print(f"\n✅ Score {report.total}/100 ≥ threshold {threshold}. No refinement needed.")
        return {
            "final_score": report.total,
            "iterations": iterations,
            "suggestions": [],
            "status": "pass",
        }

    # Collect all suggestions
    all_suggestions = []
    for dim_name, dim in [("Structure", report.structure),
                           ("Safety", report.safety),
                           ("Completeness", report.completeness),
                           ("Archetype Fit", report.archetype_fit)]:
        for s in dim.suggestions:
            all_suggestions.append({
                "dimension": dim_name,
                "suggestion": s,
                "impact": dim.max_score - dim.score,
            })

    # Sort by impact (highest first)
    all_suggestions.sort(key=lambda x: x["impact"], reverse=True)

    print(f"\n⚠️  Score {report.total}/100 < threshold {threshold}")
    print(f"\n📋 Improvement Plan ({len(all_suggestions)} items, sorted by impact):")
    for i, s in enumerate(all_suggestions, 1):
        print(f"  {i}. [{s['dimension']}] {s['suggestion']} (impact: ~{s['impact']}pt)")

    return {
        "final_score": report.total,
        "iterations": iterations,
        "suggestions": all_suggestions,
        "status": "needs_improvement",
    }


def llm_refine(filepath: str, threshold: int = 80) -> dict:
    """
    LLM-based refinement using Hermēneus execute /dia-.
    Generates a critique CCL expression and attempts execution.
    """
    content = Path(filepath).read_text(encoding="utf-8")
    report = score_prompt(filepath)

    if report.total >= threshold:
        print(f"\n✅ Score {report.total}/100 ≥ threshold {threshold}. LLM refine skipped.")
        return {"status": "pass", "score": report.total}

    # Build context for Hermēneus
    weak_dimensions = []
    for dim_name, dim in [("Structure", report.structure),
                           ("Safety", report.safety),
                           ("Completeness", report.completeness),
                           ("Archetype Fit", report.archetype_fit)]:
        if dim.normalized < 70:
            weak_dimensions.append(f"{dim_name} ({dim.normalized}/100)")

    context = (
        f"以下のプロンプトファイルの品質レビューを行え。\n"
        f"ファイル: {filepath}\n"
        f"現在スコア: {report.total}/100 (Grade: {report.grade})\n"
        f"弱い次元: {', '.join(weak_dimensions)}\n"
        f"検出 Archetype: {report.detected_archetype or 'N/A'}\n"
        f"検出フォーマット: {report.detected_format}\n\n"
        f"--- プロンプト内容 (先頭2000文字) ---\n"
        f"{content[:2000]}\n"
        f"--- ここまで ---\n\n"
        f"改善点を具体的に列挙し、修正案を提示せよ。"
    )

    # Try Hermēneus MCP execute
    print(f"\n🤖 LLM Self-Refine: Hermēneus execute /dia- を試行...")
    print(f"   Context: {len(context)} chars")
    print(f"   CCL: /dia-")

    try:
        # Use hermeneus CLI directly
        result = subprocess.run(
            [
                sys.executable, "-m", "hermeneus.src.cli",
                "execute", "/dia-",
                "--context", context,
                "--no-verify",
            ],
            capture_output=True, text=True, timeout=60,
            cwd=str(Path(__file__).parent.parent.parent.parent),
            env={**__import__("os").environ, "PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        )

        if result.returncode == 0:
            print(f"\n📝 Hermēneus /dia- 結果:")
            print(result.stdout[:3000])
            return {
                "status": "llm_critique_done",
                "score": report.total,
                "critique": result.stdout[:3000],
            }
        else:
            print(f"\n⚠️  Hermēneus 実行エラー: {result.stderr[:500]}")
            print("   → MCP 経由での実行を推奨: mcp_hermeneus_hermeneus_execute(ccl='/dia-', context=...)")
            return {
                "status": "llm_fallback",
                "score": report.total,
                "error": result.stderr[:500],
                "fallback_instruction": (
                    "Claude セッション内で以下を実行してください:\n"
                    f"  1. prompt_quality_scorer.py {filepath} -v でスコア確認\n"
                    f"  2. /dia- で批評\n"
                    f"  3. 改善を適用\n"
                    f"  4. 再スコアリング"
                ),
            }
    except subprocess.TimeoutExpired:
        print("\n⚠️  Hermēneus 実行タイムアウト (60s)")
        return {"status": "timeout", "score": report.total}
    except FileNotFoundError:
        print("\n⚠️  Hermēneus CLI が見つかりません")
        print("   → MCP 経由での実行を推奨")
        return {
            "status": "cli_not_found",
            "score": report.total,
            "fallback_instruction": (
                "MCP 経由で実行してください:\n"
                "  mcp_hermeneus_hermeneus_execute(ccl='/dia-', context='...')"
            ),
        }


def full_refine(filepath: str, threshold: int = 80, max_iter: int = 3) -> dict:
    """Run static analysis first, then LLM refinement if needed."""
    print("=" * 60)
    print("Phase 1: Static Analysis")
    print("=" * 60)
    static_result = static_refine(filepath, threshold, max_iter)

    if static_result["status"] == "pass":
        return static_result

    print(f"\n{'=' * 60}")
    print("Phase 2: LLM Self-Refine")
    print("=" * 60)
    llm_result = llm_refine(filepath, threshold)

    return {
        "static": static_result,
        "llm": llm_result,
        "final_score": static_result["final_score"],
        "status": "full_refine_done",
    }


def main():
    parser = argparse.ArgumentParser(description="Self-Refine Pipeline")
    parser.add_argument("--input", required=True, help="Input prompt file")
    parser.add_argument("--mode", choices=["static", "llm", "full"], default="full",
                        help="Refinement mode (default: full)")
    parser.add_argument("--threshold", type=int, default=80,
                        help="Quality threshold (default: 80)")
    parser.add_argument("--max-iterations", type=int, default=3,
                        help="Max static refinement iterations (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    if args.mode == "static":
        result = static_refine(args.input, args.threshold, args.max_iterations)
    elif args.mode == "llm":
        result = llm_refine(args.input, args.threshold)
    else:
        result = full_refine(args.input, args.threshold, args.max_iterations)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
