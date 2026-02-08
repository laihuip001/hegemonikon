#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/
# PURPOSE: FEP E2E v2 30分耐久テスト — 自律学習の証明
"""
FEP E2E Endurance Test — 30分放置テスト

多様な入力を繰り返し投入し、Agent の学習過程を記録する。
A行列は永続化され、セッションを跨いで蓄積される。

Usage:
    python scripts/e2e_endurance.py --minutes 30
    python scripts/e2e_endurance.py --minutes 5 --cpu  # 短縮版

Output:
    logs/e2e_endurance_<timestamp>.jsonl
"""

import argparse
import json
import logging
import random
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("e2e_endurance")


# Diverse inputs covering all Series
INPUTS = [
    # O-series (Ousia)
    "なぜこのプロジェクトは存在するのか",
    "美とは何か。この問いの本質を深く考えたい",
    "目標を再定義したい。今の方向性は正しいか",
    "実装計画を立てて段階的に進めたい",
    # S-series (Stratēgia)
    "適切な粒度を決めたい。マクロかミクロか",
    "どの手法を使うべきか。選択肢を整理してほしい",
    "評価基準を明確にしたい。成功とは何か",
    "理論と実践のバランスをどう取るか",
    # H-series (Hormē)
    "直感的に違和感がある。何かがおかしい",
    "この判断に自信がない。確信度を上げる方法は",
    "モチベーションが下がっている。何を望んでいるか",
    "信念が揺らいでいる。根拠を再確認したい",
    # P-series (Peristasis)
    "スコープを絞りたい。何に集中すべきか",
    "ゴールへの最短経路を設計してほしい",
    "進捗のリズムを作りたい。サイクルを定義する",
    "どの技法が最適か。ツールの選定をしたい",
    # K-series (Kairos)
    "今このタイミングで着手すべきか",
    "期限を設定したい。いつまでに完了するか",
    "そもそもの目的を問い直したい",
    "先行研究を調べてから判断したい",
    # A-series (Axiologikē)
    "感情的に引っかかることがある。整理したい",
    "批判的にレビューしてほしい。問題点を指摘して",
    "この経験から学べる原則は何か",
    "確立された知識と照らし合わせて確認したい",
    # Mixed / Complex
    "テストが失敗している。原因を調査して修正したい",
    "新機能を追加したいが、リスクも心配だ",
    "コードの品質を上げたい。リファクタリングの方針は",
    "ドキュメントが不足している。何を書くべきか",
]


def run_endurance(
    minutes: int = 30,
    force_cpu: bool = False,
):
    """Run endurance test for specified minutes."""
    from mekhane.fep.e2e_loop import run_loop_v2

    # Persistent A matrix
    a_matrix_dir = Path.home() / "oikos/hegemonikon/data/fep"
    a_matrix_dir.mkdir(parents=True, exist_ok=True)
    a_matrix_path = str(a_matrix_dir / "endurance_A.npy")

    # Log file
    log_dir = Path.home() / "oikos/hegemonikon/logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"e2e_endurance_{ts}.jsonl"

    logger.info(f"═══ E2E Endurance Test ═══")
    logger.info(f"Duration: {minutes} min")
    logger.info(f"A-matrix: {a_matrix_path}")
    logger.info(f"Log: {log_path}")
    logger.info(f"Inputs: {len(INPUTS)} patterns")
    logger.info("")

    start = time.time()
    end_time = start + minutes * 60
    total_cycles = 0
    total_errors = 0

    shuffled = list(INPUTS)

    with open(log_path, "w") as f:
        while time.time() < end_time:
            random.shuffle(shuffled)

            for text in shuffled:
                if time.time() >= end_time:
                    break

                try:
                    result = run_loop_v2(
                        text,
                        cycles=2,
                        a_matrix_path=a_matrix_path,
                        force_cpu=force_cpu,
                    )

                    for c in result.cycles:
                        entry = {
                            "ts": datetime.now().isoformat(),
                            "input": text[:50],
                            "cycle": c.cycle,
                            "action": c.action_name,
                            "series": c.selected_series,
                            "attractor": c.attractor_series,
                            "entropy": round(c.fep_entropy, 4),
                            "confidence": round(c.fep_confidence, 3),
                            "cone_dispersion": c.cone_dispersion,
                            "a_updated": c.a_matrix_updated,
                        }
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                        total_cycles += 1

                    if result.learning_proof:
                        logger.info(
                            f"[{total_cycles:4d}] {text[:30]}... → "
                            f"{result.cycles[-1].action_name} "
                            f"[{result.cycles[-1].selected_series or '-'}] "
                            f"| {result.learning_proof[:60]}"
                        )
                    else:
                        logger.info(
                            f"[{total_cycles:4d}] {text[:30]}... → "
                            f"{result.cycles[-1].action_name} "
                            f"[{result.cycles[-1].selected_series or '-'}]"
                        )

                    f.flush()

                except Exception as e:
                    total_errors += 1
                    logger.warning(f"Error: {e}")
                    entry = {
                        "ts": datetime.now().isoformat(),
                        "input": text[:50],
                        "error": str(e),
                    }
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    f.flush()

    elapsed = time.time() - start
    logger.info("")
    logger.info(f"═══ Endurance Test Complete ═══")
    logger.info(f"Elapsed: {elapsed/60:.1f} min")
    logger.info(f"Total cycles: {total_cycles}")
    logger.info(f"Errors: {total_errors}")
    logger.info(f"Throughput: {total_cycles/elapsed*60:.1f} cycles/min")
    logger.info(f"Log: {log_path}")


def main():
    parser = argparse.ArgumentParser(description="FEP E2E Endurance Test")
    parser.add_argument(
        "--minutes", type=int, default=30,
        help="Test duration in minutes (default: 30)",
    )
    parser.add_argument("--cpu", action="store_true", help="Force CPU")
    args = parser.parse_args()

    run_endurance(minutes=args.minutes, force_cpu=args.cpu)


if __name__ == "__main__":
    main()
