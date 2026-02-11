#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/fep/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

Basin Learning ループの検証。
BasinLogger bias → BasinLearner → weight adjustments → round-trip。
"""

import pytest
from pathlib import Path
from datetime import datetime

from mekhane.fep.basin_logger import BasinBias
from mekhane.fep.basin_learner import (
    BasinLearner,
    WeightAdjustment,
    LearningEpoch,
    DEFAULT_LEARNING_RATE,
    MAX_ADJUSTMENT,
    MIN_CONSISTENT_SIGNALS,
)


# =============================================================================
# Helpers
# =============================================================================


# PURPOSE: Verify make biases behaves correctly
def make_biases(**kwargs) -> dict[str, BasinBias]:
    """テスト用 bias 辞書を生成。"""
    biases = {}
    for series, (over, under, correct, total) in kwargs.items():
        b = BasinBias(series=series)
        b.over_predict_count = over
        b.under_predict_count = under
        b.correct_count = correct
        b.total_count = total
        biases[series] = b
    return biases


# =============================================================================
# Weight Adjustment
# =============================================================================


# PURPOSE: Test suite validating weight adjustment correctness
class TestWeightAdjustment:
    """重み補正の基本テスト。"""

    # PURPOSE: Verify too wide contracts behaves correctly
    def test_too_wide_contracts(self):
        """Basin が広すぎる → contract。"""
        biases = make_biases(O=(8, 0, 2, 10))  # precision=0.2
        learner = BasinLearner()
        epoch = learner.learn_from_biases(biases)

        assert len(epoch.adjustments) == 1
        adj = epoch.adjustments[0]
        assert adj.series == "O"
        assert adj.direction == "contract"
        assert adj.magnitude > 0

    # PURPOSE: Verify too narrow expands behaves correctly
    def test_too_narrow_expands(self):
        """Basin が狭すぎる → expand。"""
        biases = make_biases(S=(0, 8, 2, 10))  # recall=0.2
        learner = BasinLearner()
        epoch = learner.learn_from_biases(biases)

        assert len(epoch.adjustments) == 1
        adj = epoch.adjustments[0]
        assert adj.series == "S"
        assert adj.direction == "expand"
        assert adj.magnitude > 0

    # PURPOSE: Verify balanced no adjustment behaves correctly
    def test_balanced_no_adjustment(self):
        """バランスが取れている → 調整なし。"""
        biases = make_biases(A=(1, 1, 8, 10))  # precision=0.8, recall=0.8
        learner = BasinLearner()
        epoch = learner.learn_from_biases(biases)

        assert len(epoch.adjustments) == 0

    # PURPOSE: Verify insufficient data skipped behaves correctly
    def test_insufficient_data_skipped(self):
        """データ不足 → スキップ。"""
        biases = make_biases(H=(2, 0, 0, 2))  # total < MIN_CONSISTENT_SIGNALS
        learner = BasinLearner()
        epoch = learner.learn_from_biases(biases)

        assert len(epoch.adjustments) == 0

    # PURPOSE: Verify magnitude capped behaves correctly
    def test_magnitude_capped(self):
        """補正量は MAX_ADJUSTMENT 以下。"""
        biases = make_biases(K=(100, 0, 0, 100))  # precision=0.0
        learner = BasinLearner(learning_rate=1.0)
        epoch = learner.learn_from_biases(biases)

        for adj in epoch.adjustments:
            assert adj.magnitude <= MAX_ADJUSTMENT


# =============================================================================
# Weight Persistence
# =============================================================================


# PURPOSE: Test suite validating weight persistence correctness
class TestWeightPersistence:
    """学習履歴 round-trip テスト。"""

    # PURPOSE: Verify save load roundtrip behaves correctly
    def test_save_load_roundtrip(self, tmp_path):
        """重みを保存→復元。"""
        learner = BasinLearner(history_path=tmp_path / "adj.yaml")
        biases = make_biases(
            O=(8, 0, 2, 10),
            S=(0, 8, 2, 10),
        )
        learner.learn_from_biases(biases)
        learner.save_history()

        learner2 = BasinLearner(history_path=tmp_path / "adj.yaml")
        loaded = learner2.load_history()
        assert loaded == 1
        assert "O" in learner2.current_weights
        assert "S" in learner2.current_weights

    # PURPOSE: Verify load nonexistent behaves correctly
    def test_load_nonexistent(self, tmp_path):
        """存在しないファイル → 0。"""
        learner = BasinLearner()
        loaded = learner.load_history(tmp_path / "nope.yaml")
        assert loaded == 0


# =============================================================================
# Weight Overrides
# =============================================================================


# PURPOSE: Test suite validating weight overrides correctness
class TestWeightOverrides:
    """SeriesAttractor 互換重みテスト。"""

    # PURPOSE: Verify no overrides initially behaves correctly
    def test_no_overrides_initially(self):
        """初期状態 → 空。"""
        learner = BasinLearner()
        assert learner.get_weight_overrides() == {}

    # PURPOSE: Verify overrides after learning behaves correctly
    def test_overrides_after_learning(self):
        """学習後 → override のある Series のみ。"""
        biases = make_biases(O=(8, 0, 2, 10))
        learner = BasinLearner()
        learner.learn_from_biases(biases)

        overrides = learner.get_weight_overrides()
        assert "O" in overrides
        assert overrides["O"] < 1.0  # contracted

    # PURPOSE: Verify weight bounds behaves correctly
    def test_weight_bounds(self):
        """重みは 0.5 ~ 2.0 の範囲内。"""
        biases = make_biases(P=(100, 0, 0, 100))
        learner = BasinLearner(learning_rate=1.0)

        for _ in range(20):
            learner.learn_from_biases(biases)

        for w in learner.current_weights.values():
            assert 0.5 <= w <= 2.0


# =============================================================================
# Multiple Epochs
# =============================================================================


# PURPOSE: Test suite validating multiple epochs correctness
class TestMultipleEpochs:
    """複数エポックの学習テスト。"""

    # PURPOSE: Verify epoch count increments behaves correctly
    def test_epoch_count_increments(self):
        """エポックカウントが増加。"""
        biases = make_biases(O=(8, 0, 2, 10))
        learner = BasinLearner()
        learner.learn_from_biases(biases)
        learner.learn_from_biases(biases)
        assert learner.epoch_count == 2

    # PURPOSE: Verify weights converge behaves correctly
    def test_weights_converge(self):
        """同じ bias で繰り返し学習 → 重みが変化方向に収束。"""
        biases = make_biases(O=(8, 0, 2, 10))
        learner = BasinLearner()

        weights = []
        for _ in range(5):
            learner.learn_from_biases(biases)
            weights.append(learner.current_weights.get("O", 1.0))

        # monotonically decreasing (contracting)
        for i in range(1, len(weights)):
            assert weights[i] <= weights[i - 1]


# =============================================================================
# Summary Formatting
# =============================================================================


# PURPOSE: Test suite validating summary format correctness
class TestSummaryFormat:
    """サマリー出力テスト。"""

    # PURPOSE: Verify no epochs summary behaves correctly
    def test_no_epochs_summary(self):
        """エポックなし → 'No epochs'。"""
        learner = BasinLearner()
        summary = learner.format_summary()
        assert "No epochs" in summary

    # PURPOSE: Verify summary with overrides behaves correctly
    def test_summary_with_overrides(self):
        """override あり → テーブルに表示。"""
        biases = make_biases(O=(8, 0, 2, 10))
        learner = BasinLearner()
        learner.learn_from_biases(biases)

        summary = learner.format_summary()
        assert "Basin Learning" in summary
        assert "O" in summary
