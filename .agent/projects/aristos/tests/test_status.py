# F6: Aristos Status API テスト
"""
get_aristos_status() が正しくフィードバック統計と
evolved weights 情報を集約することを検証。
"""
import json
from pathlib import Path

import pytest
from aristos.route_feedback import RouteFeedback, log_route_feedback
from aristos.status import (
    AristosStatus,
    EvolvedWeightsInfo,
    FeedbackStats,
    get_aristos_status,
    get_evolved_weights_info,
    get_feedback_stats,
)


@pytest.fixture
def tmp_paths(tmp_path):
    return {
        "feedback": tmp_path / "route_feedback.yaml",
        "weights": tmp_path / "cost_weights.json",
    }


def _create_feedback(tmp_fb_path, n=5, base_quality=0.8):
    """テスト用フィードバックを生成"""
    for i in range(n):
        fb = RouteFeedback(
            source=f"wf{i}",
            target=f"wf{i+1}",
            chosen_route=[f"wf{i}", f"wf{i+1}"],
            quality=max(0.0, min(1.0, base_quality - i * 0.2)),
            depth=f"L{i % 4}",
        )
        log_route_feedback(fb, path=tmp_fb_path)


def _create_weights(path, weights=None, fitness_scalar=0.75, gen=10):
    """テスト用 evolved weights を生成"""
    data = {
        "cost_weights": weights or {"pt": 1.2, "depth": 1.8, "time_min": 0.6},
        "fitness": {"scalar": fitness_scalar},
        "generation": gen,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


class TestFeedbackStats:
    """フィードバック統計テスト"""

    def test_empty_feedback(self, tmp_paths):
        stats = get_feedback_stats(tmp_paths["feedback"])
        assert stats.total_count == 0
        assert stats.avg_quality == 0.0

    def test_stats_calculation(self, tmp_paths):
        _create_feedback(tmp_paths["feedback"], n=5, base_quality=0.8)
        stats = get_feedback_stats(tmp_paths["feedback"])
        assert stats.total_count == 5
        assert 0.0 < stats.avg_quality < 1.0
        assert stats.high_quality_count >= 1  # quality=0.8 > 0.7
        assert stats.low_quality_count >= 1   # quality=0.0 < 0.3

    def test_depth_distribution(self, tmp_paths):
        _create_feedback(tmp_paths["feedback"], n=4)
        stats = get_feedback_stats(tmp_paths["feedback"])
        assert sum(stats.depth_distribution.values()) == 4


class TestEvolvedWeightsInfo:
    """進化済み重みテスト"""

    def test_no_weights_file(self, tmp_paths):
        info = get_evolved_weights_info(tmp_paths["weights"])
        assert info.available is False
        assert info.weights == {}

    def test_load_weights(self, tmp_paths):
        _create_weights(tmp_paths["weights"])
        info = get_evolved_weights_info(tmp_paths["weights"])
        assert info.available is True
        assert "pt" in info.weights
        assert info.fitness_scalar == 0.75
        assert info.generation == 10

    def test_corrupt_json(self, tmp_paths):
        tmp_paths["weights"].write_text("not json")
        info = get_evolved_weights_info(tmp_paths["weights"])
        assert info.available is False


class TestAristosStatus:
    """統合ステータステスト"""

    def test_empty_status(self, tmp_paths):
        status = get_aristos_status(
            feedback_path=tmp_paths["feedback"],
            weights_path=tmp_paths["weights"],
        )
        assert status.feedback.total_count == 0
        assert status.evolved_weights.available is False
        assert len(status.default_weights) == 5

    def test_full_status(self, tmp_paths):
        _create_feedback(tmp_paths["feedback"], n=3, base_quality=0.9)
        _create_weights(tmp_paths["weights"])

        status = get_aristos_status(
            feedback_path=tmp_paths["feedback"],
            weights_path=tmp_paths["weights"],
        )
        assert status.feedback.total_count == 3
        assert status.evolved_weights.available is True

    def test_to_dict(self, tmp_paths):
        _create_feedback(tmp_paths["feedback"], n=2)
        _create_weights(tmp_paths["weights"])

        status = get_aristos_status(
            feedback_path=tmp_paths["feedback"],
            weights_path=tmp_paths["weights"],
        )
        d = status.to_dict()
        assert isinstance(d, dict)
        assert "feedback" in d
        assert "evolved_weights" in d
        assert "default_weights" in d
        assert isinstance(d["feedback"]["total_count"], int)
