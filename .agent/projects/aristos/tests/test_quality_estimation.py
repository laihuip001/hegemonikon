# F4: estimate_quality のパラメトリックテスト
"""
estimate_quality ヒューリスティクスの妥当性検証:
- 境界値テスト
- 全組み合わせパラメトリック
- 出力範囲不変条件
"""
import itertools
import pytest
from aristos.route_feedback import estimate_quality


class TestEstimateQualityBounds:
    """出力が常に [0.0, 1.0] 範囲内であることの不変条件"""

    @pytest.mark.parametrize("actual_time", [0.0, 0.1, 1.0, 5.0, 100.0])
    @pytest.mark.parametrize("estimated_time", [0.0, 1.0, 5.0, 30.0])
    @pytest.mark.parametrize("had_errors", [True, False])
    @pytest.mark.parametrize("was_corrected", [True, False])
    @pytest.mark.parametrize("depth", ["L0", "L1", "L2", "L3"])
    def test_output_range(
        self, actual_time, estimated_time, had_errors, was_corrected, depth,
    ):
        q = estimate_quality(
            actual_time_min=actual_time,
            estimated_time_min=estimated_time,
            had_errors=had_errors,
            was_corrected=was_corrected,
            depth=depth,
        )
        assert 0.0 <= q <= 1.0, f"quality={q} out of bounds"


class TestEstimateQualityBaseline:
    """ベースライン品質のテスト"""

    def test_default_no_inputs(self):
        """入力なし → baseline 0.7"""
        q = estimate_quality()
        assert q == 0.7

    def test_perfect_execution(self):
        """高速完了、エラーなし → 高品質"""
        q = estimate_quality(
            actual_time_min=3.0,
            estimated_time_min=5.0,
            had_errors=False,
            was_corrected=False,
        )
        assert q == 0.9  # 0.7 + 0.2 (faster than expected)

    def test_slightly_over_time(self):
        """やや超過 → やや高品質"""
        q = estimate_quality(
            actual_time_min=7.0,
            estimated_time_min=5.0,
            had_errors=False,
            was_corrected=False,
        )
        assert q == 0.8  # 0.7 + 0.1 (ratio=1.4, <= 1.5)

    def test_significantly_over_time(self):
        """大幅超過 → 品質低下"""
        q = estimate_quality(
            actual_time_min=10.0,
            estimated_time_min=5.0,
            had_errors=False,
            was_corrected=False,
        )
        assert q == 0.6  # 0.7 - 0.1 (ratio=2.0, > 1.5)


class TestEstimateQualityPenalties:
    """ペナルティの適用テスト"""

    def test_error_penalty(self):
        """エラー → -0.3"""
        q = estimate_quality(had_errors=True)
        assert q == 0.4  # 0.7 - 0.3

    def test_correction_penalty(self):
        """修正 → -0.2"""
        q = estimate_quality(was_corrected=True)
        assert q == 0.5  # 0.7 - 0.2

    def test_both_penalties(self):
        """エラー + 修正 → -0.5, clamped to 0.2"""
        q = estimate_quality(had_errors=True, was_corrected=True)
        assert q == 0.2  # 0.7 - 0.3 - 0.2

    def test_worst_case_clamped(self):
        """全ペナルティ + 時間超過 → 0.1 (clamp)"""
        q = estimate_quality(
            actual_time_min=100.0,
            estimated_time_min=5.0,
            had_errors=True,
            was_corrected=True,
        )
        assert q == 0.1  # 0.7 - 0.1 - 0.3 - 0.2 = 0.1


class TestEstimateQualityDepth:
    """深度ボーナスのテスト"""

    def test_l3_bonus(self):
        """L3 + エラーなし → +0.1"""
        q = estimate_quality(depth="L3", had_errors=False)
        assert q == 0.8  # 0.7 + 0.1

    def test_l3_no_bonus_on_error(self):
        """L3 + エラーあり → ボーナスなし"""
        q = estimate_quality(depth="L3", had_errors=True)
        assert q == 0.4  # 0.7 - 0.3 (no L3 bonus)

    def test_l2_no_bonus(self):
        """L2 → ボーナスなし"""
        q = estimate_quality(depth="L2", had_errors=False)
        assert q == 0.7

    def test_l3_perfect(self):
        """L3 完走 + 高速完了 → 最高品質"""
        q = estimate_quality(
            actual_time_min=3.0,
            estimated_time_min=5.0,
            depth="L3",
        )
        assert q == 1.0  # 0.7 + 0.2 + 0.1 = 1.0


class TestEstimateQualityEdgeCases:
    """エッジケース"""

    def test_zero_estimated_time(self):
        """推定時間0 → 時間効率計算スキップ"""
        q = estimate_quality(actual_time_min=5.0, estimated_time_min=0.0)
        assert q == 0.7  # baseline

    def test_zero_actual_time(self):
        """実際時間0 → 時間効率計算スキップ"""
        q = estimate_quality(actual_time_min=0.0, estimated_time_min=5.0)
        assert q == 0.7  # baseline

    def test_exact_time_match(self):
        """推定時間 = 実際時間 → faster 扱い"""
        q = estimate_quality(actual_time_min=5.0, estimated_time_min=5.0)
        assert q == 0.9  # ratio=1.0, <= 1.0 → +0.2
