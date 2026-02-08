#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/
# PURPOSE: FEP E2E Loop のデモ実行
"""
FEP E2E Demo — 動く認知体のデモンストレーション

Usage:
    python scripts/e2e_demo.py "なぜこのプロジェクトは存在するのか"
    python scripts/e2e_demo.py "設計をレビューしたい"
    python scripts/e2e_demo.py --cycles 3 "テストが失敗している"
"""

import argparse
import sys
from pathlib import Path

# Project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    parser = argparse.ArgumentParser(description="FEP E2E Loop Demo")
    parser.add_argument("input", type=str, help="自然言語入力")
    parser.add_argument("--cycles", type=int, default=2, help="ループ回数 (default: 2)")
    parser.add_argument("--cpu", action="store_true", help="CPU 強制 (GPU なし)")
    args = parser.parse_args()

    from mekhane.fep.e2e_loop import run_loop

    print(f"\n🧠 FEP E2E Loop — Active Inference Demo")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Input: {args.input}")
    print(f"Cycles: {args.cycles}")
    print()

    result = run_loop(args.input, cycles=args.cycles, force_cpu=args.cpu)

    for c in result.cycles:
        print(f"┌─[Cycle {c.cycle}]──────────────────────────────┐")
        print(f"│ Observation: {c.obs_decoded}")
        print(f"│")
        print(f"│ ── FEP Agent (メタ判断) ──")
        print(f"│   Action:     {'🔴 observe' if c.fep_action == 'observe' else '🟢 act'}")
        print(f"│   Entropy:    {c.fep_entropy:.3f}")
        print(f"│   Confidence: {c.fep_confidence:.0%}")
        if c.should_epoche:
            print(f"│   ⚠️  Auto-Epochē: 判断停止を推奨")
        print(f"│")
        print(f"│ ── Attractor (コンテンツ判断) ──")
        if c.dispatch_wf:
            print(f"│   WF:         {c.dispatch_wf}")
            print(f"│   Series:     {c.dispatch_series}")
            print(f"│   Oscillation:{c.dispatch_oscillation}")
            if c.dispatch_alternatives:
                print(f"│   Alts:       {', '.join(c.dispatch_alternatives)}")
            print(f"│   Reason:     {c.dispatch_reason[:80]}")
        else:
            print(f"│   (引力圏外 — 既存 Series にマッチせず)")
        print(f"│")
        if c.cone_apex:
            print(f"│ ── Cone (シミュレーション) ──")
            print(f"│   Apex:       {c.cone_apex[:60]}")
            print(f"│   Dispersion: {c.cone_dispersion:.3f}")
            print(f"│   Method:     {c.cone_method}")
        print(f"│")
        print(f"│ A-matrix: {'✅ updated' if c.a_matrix_updated else '—'}")
        print(f"└────────────────────────────────────────┘")
        print()

    if result.learning_proof:
        print(f"═══ Learning Proof ═══")
        print(f"📈 {result.learning_proof}")
        print()

    print(result.summary)


if __name__ == "__main__":
    main()
