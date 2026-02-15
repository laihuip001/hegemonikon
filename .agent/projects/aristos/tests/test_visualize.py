# F14: Visualize テスト
"""
aristos.visualize モジュールのテスト
"""
import pytest
from aristos.visualize import (
    render_quality_histogram,
    render_weight_comparison,
    render_depth_distribution,
)


class TestQualityHistogram:
    """品質ヒストグラム"""

    def test_empty_data(self):
        result = render_quality_histogram([])
        assert "データなし" in result

    def test_uniform_distribution(self):
        qualities = [i / 10 for i in range(10)]
        result = render_quality_histogram(qualities)
        assert "n=10" in result
        assert "█" in result

    def test_all_same_quality(self):
        result = render_quality_histogram([0.5] * 20)
        assert "n=20" in result

    def test_bins_param(self):
        qualities = [0.1, 0.5, 0.9]
        result = render_quality_histogram(qualities, bins=5)
        assert "n=3" in result

    def test_edge_value_one(self):
        """quality=1.0 でインデックスオーバーフローしない"""
        result = render_quality_histogram([1.0, 1.0, 1.0])
        assert "n=3" in result


class TestWeightComparison:
    """重み比較"""

    def test_empty_both(self):
        result = render_weight_comparison({}, {})
        assert "データなし" in result

    def test_basic_comparison(self):
        evolved = {"pt": 1.5, "depth": 3.0}
        default = {"pt": 1.0, "depth": 2.0}
        result = render_weight_comparison(evolved, default)
        assert "pt" in result
        assert "depth" in result
        assert "evolved" in result
        assert "default" in result

    def test_diff_markers(self):
        evolved = {"x": 2.0, "y": 0.5, "z": 1.0}
        default = {"x": 1.0, "y": 1.5, "z": 1.0}
        result = render_weight_comparison(evolved, default)
        assert "↑" in result  # x increased
        assert "↓" in result  # y decreased


class TestDepthDistribution:
    """深度分布"""

    def test_empty(self):
        result = render_depth_distribution({})
        assert "データなし" in result

    def test_basic(self):
        dist = {"L0": 5, "L1": 10, "L2": 20, "L3": 3}
        result = render_depth_distribution(dist)
        assert "total=38" in result
        assert "L2" in result
        assert "%" in result

    def test_single_depth(self):
        result = render_depth_distribution({"L2": 7})
        assert "total=7" in result
        assert "100%" in result
