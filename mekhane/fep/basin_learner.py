#!/usr/bin/env python3
# PROOF: [L2/FEP] <- mekhane/fep/
# PURPOSE: Basin の bias データから prototype を自動補正する学習ループ
"""
PROOF: [L2/FEP] このファイルは存在しなければならない

BasinLogger が収集した bias データ → BasinLearner が prototype を補正
→ Attractor の推薦精度が向上 → 非等方的 basin の実現

Q.E.D.

Basin Learner — 異方的Basin学習ループ

BasinLogger.suggestions_for_tuning() の出力を消費し、
SeriesAttractor の prototype weights を補正する閉ループ学習。

Architecture:
    BasinLogger → bias_report → BasinLearner → weight_adjustments
    → SeriesAttractor に適用 → 次の推薦精度が向上
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import json
import yaml


# =============================================================================
# Constants
# =============================================================================

# ⚠️ PROVISIONAL: 以下は全て仮値。実使用データ収集後に calibration すべき。
# Calibration Plan:
#   1. 100+ correction ログが蓄積されたら A/B テスト
#   2. lr を 0.01-0.10 の範囲で探索
#   3. MAX_ADJUSTMENT を precision/recall の収束速度で調整

# 学習率 (conservative: 急激な変化を防ぐ)
DEFAULT_LEARNING_RATE = 0.05  # PROVISIONAL
# bias_direction がこの回数以上 consistent なら補正を適用
MIN_CONSISTENT_SIGNALS = 3  # PROVISIONAL
# 補正の最大変幅 (1回あたり)
MAX_ADJUSTMENT = 0.15  # PROVISIONAL
# 補正履歴の保存先
DEFAULT_ADJUSTMENTS_PATH = (
    Path.home() / "oikos/mneme/.hegemonikon/basin/adjustments.yaml"
)


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class WeightAdjustment:
    """1つの Series に対する重み補正。"""

    series: str
    direction: str  # "expand" or "contract"
    magnitude: float  # 0.0 ~ MAX_ADJUSTMENT
    reason: str
    applied_at: Optional[str] = None


@dataclass
class LearningEpoch:
    """1回の学習サイクルの結果。"""

    epoch: int
    timestamp: str
    adjustments: List[WeightAdjustment] = field(default_factory=list)
    total_corrections: int = 0
    precision_before: Dict[str, float] = field(default_factory=dict)
    precision_after: Dict[str, float] = field(default_factory=dict)


# =============================================================================
# BasinLearner
# =============================================================================


class BasinLearner:
    """Basin の bias から prototype weights を学習する。

    Usage:
        from mekhane.fep.basin_logger import BasinLogger
        logger = BasinLogger()
        logger.load_biases(log_file)

        learner = BasinLearner()
        epoch = learner.learn_from_biases(logger)
        learner.save_history()
    """

    def __init__(
        self,
        learning_rate: float = DEFAULT_LEARNING_RATE,
        history_path: Optional[Path] = None,
    ):
        self._lr = learning_rate
        self._history_path = history_path or DEFAULT_ADJUSTMENTS_PATH
        self._epochs: List[LearningEpoch] = []
        self._current_weights: Dict[str, float] = {}  # series -> weight multiplier

    @property
    def epoch_count(self) -> int:
        """完了したエポック数。"""
        return len(self._epochs)

    @property
    def current_weights(self) -> Dict[str, float]:
        """現在の重み乗数。"""
        return dict(self._current_weights)

    # PURPOSE: BasinLogger の bias データから学習する
    def learn_from_biases(
        self,
        biases: Dict[str, "BasinBias"],  # type: ignore[name-defined]
    ) -> LearningEpoch:
        """BasinLogger の bias データから prototype weights を補正する。

        Args:
            biases: BasinLogger._biases (series -> BasinBias)

        Returns:
            LearningEpoch with adjustments
        """
        epoch = LearningEpoch(
            epoch=self.epoch_count + 1,
            timestamp=datetime.now().isoformat(),
        )

        for series, bias in biases.items():
            # データ不足はスキップ
            if bias.total_count < MIN_CONSISTENT_SIGNALS:
                continue

            direction = bias.bias_direction
            if direction == "balanced":
                continue

            # 補正量を計算
            if direction == "too_wide":
                # Basin が広すぎる → 重みを下げて範囲を狭める
                magnitude = min(
                    self._lr * (1 - bias.precision),
                    MAX_ADJUSTMENT,
                )
                adj = WeightAdjustment(
                    series=series,
                    direction="contract",
                    magnitude=magnitude,
                    reason=f"precision={bias.precision:.2f}, over_predict={bias.over_predict_count}",
                )
            else:  # too_narrow
                # Basin が狭すぎる → 重みを上げて範囲を広げる
                magnitude = min(
                    self._lr * (1 - bias.recall),
                    MAX_ADJUSTMENT,
                )
                adj = WeightAdjustment(
                    series=series,
                    direction="expand",
                    magnitude=magnitude,
                    reason=f"recall={bias.recall:.2f}, under_predict={bias.under_predict_count}",
                )

            # 記録前のprecision
            epoch.precision_before[series] = bias.precision

            # 重み乗数を更新
            current = self._current_weights.get(series, 1.0)
            if adj.direction == "contract":
                new_weight = max(0.5, current - adj.magnitude)
            else:
                new_weight = min(2.0, current + adj.magnitude)

            self._current_weights[series] = new_weight
            adj.applied_at = datetime.now().isoformat()
            epoch.adjustments.append(adj)
            epoch.total_corrections += 1

        self._epochs.append(epoch)
        return epoch

    # PURPOSE: 学習履歴を YAML ファイルに保存
    def save_history(self, path: Optional[Path] = None) -> Path:
        """学習履歴を YAML ファイルに保存。"""
        target = path or self._history_path
        target.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "current_weights": self._current_weights,
            "epoch_count": self.epoch_count,
            "epochs": [
                {
                    "epoch": e.epoch,
                    "timestamp": e.timestamp,
                    "total_corrections": e.total_corrections,
                    "adjustments": [
                        {
                            "series": a.series,
                            "direction": a.direction,
                            "magnitude": a.magnitude,
                            "reason": a.reason,
                        }
                        for a in e.adjustments
                    ],
                }
                for e in self._epochs
            ],
        }

        target.write_text(
            yaml.dump(data, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
        return target

    # PURPOSE: YAML ファイルから学習履歴を復元
    def load_history(self, path: Optional[Path] = None) -> int:
        """YAML ファイルから学習履歴を復元。

        Returns:
            復元したエポック数
        """
        target = path or self._history_path
        if not target.exists():
            return 0

        data = yaml.safe_load(target.read_text(encoding="utf-8"))
        if not data:
            return 0

        self._current_weights = data.get("current_weights", {})
        return data.get("epoch_count", 0)

    # PURPOSE: 現在の重みを SeriesAttractor 互換形式で返す
    def get_weight_overrides(self) -> Dict[str, float]:
        """SeriesAttractor に渡す重み乗数を返す。

        重みが 1.0 でない Series のみ含む。
        """
        return {
            s: w for s, w in self._current_weights.items()
            if abs(w - 1.0) > 0.001
        }

    # PURPOSE: 学習サマリーを生成
    def format_summary(self) -> str:
        """学習サマリーを Markdown で返す。"""
        if not self._epochs:
            return "### Basin Learning\n\nNo epochs recorded."

        latest = self._epochs[-1]
        lines = [
            "### Basin Learning",
            f"| 項目 | 値 |",
            f"|:-----|---:|",
            f"| Epochs | {self.epoch_count} |",
            f"| Active Weights | {len(self.get_weight_overrides())} |",
            f"| Latest Corrections | {latest.total_corrections} |",
        ]

        overrides = self.get_weight_overrides()
        if overrides:
            lines.append("")
            lines.append("| Series | Weight |")
            lines.append("|:-------|-------:|")
            for s, w in sorted(overrides.items()):
                arrow = "↑" if w > 1.0 else "↓"
                lines.append(f"| {s} | {w:.3f} {arrow} |")

        return "\n".join(lines)
