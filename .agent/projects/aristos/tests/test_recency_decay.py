# F10: Recency Decay テスト
"""
PTOptimizer._convert_route_feedback の recency decay 動作を検証。
decay_rate パラメータによる confidence 重み付けの正確性をテスト。
"""
import pytest
from aristos.pt_optimizer import PTOptimizer
from aristos.route_feedback import RouteFeedback


def _make_feedbacks(n: int, quality: float = 0.8) -> list:
    """テスト用フィードバックリスト生成"""
    return [
        RouteFeedback(
            source=f"wf{i}",
            target=f"wf{i+1}",
            chosen_route=[f"wf{i}", f"wf{i+1}"],
            quality=quality,
            depth=f"L{i % 4}",
        )
        for i in range(n)
    ]


class TestRecencyDecayBasic:
    """decay 基本動作"""

    def test_no_decay(self):
        """decay_rate=1.0 → 全 fb が同じ confidence"""
        opt = PTOptimizer()
        fbs = _make_feedbacks(5, quality=0.8)
        entries = opt._convert_route_feedback(fbs, decay_rate=1.0)
        for e in entries:
            assert abs(e.confidence - 0.8) < 0.001

    def test_latest_always_full_weight(self):
        """最新 fb は常に quality * 1.0"""
        opt = PTOptimizer()
        fbs = _make_feedbacks(10, quality=0.9)
        for rate in [0.5, 0.8, 0.95, 1.0]:
            entries = opt._convert_route_feedback(fbs, decay_rate=rate)
            # 最後の entry が最新 → recency weight = 1.0
            assert abs(entries[-1].confidence - 0.9) < 0.001

    def test_oldest_decayed(self):
        """最古 fb は decay_rate^(n-1) で減衰"""
        opt = PTOptimizer()
        fbs = _make_feedbacks(5, quality=1.0)
        entries = opt._convert_route_feedback(fbs, decay_rate=0.5)
        # 最古 (index 0): 1.0 * 0.5^4 = 0.0625
        assert abs(entries[0].confidence - 0.0625) < 0.001
        # 最新 (index 4): 1.0 * 0.5^0 = 1.0
        assert abs(entries[4].confidence - 1.0) < 0.001

    def test_monotonic_increase(self):
        """confidence は古→新で単調増加 (同一 quality 時)"""
        opt = PTOptimizer()
        fbs = _make_feedbacks(8, quality=0.7)
        entries = opt._convert_route_feedback(fbs, decay_rate=0.9)
        for i in range(len(entries) - 1):
            assert entries[i].confidence <= entries[i + 1].confidence


class TestRecencyDecayEdgeCases:
    """edge case"""

    def test_single_feedback(self):
        """n=1 → decay の影響なし"""
        opt = PTOptimizer()
        fbs = _make_feedbacks(1, quality=0.6)
        entries = opt._convert_route_feedback(fbs, decay_rate=0.5)
        assert len(entries) == 1
        assert abs(entries[0].confidence - 0.6) < 0.001

    def test_empty_feedback(self):
        """空リスト → 空リスト"""
        opt = PTOptimizer()
        entries = opt._convert_route_feedback([], decay_rate=0.9)
        assert entries == []

    def test_zero_quality(self):
        """quality=0.0 → decay 後も 0.0"""
        opt = PTOptimizer()
        fbs = _make_feedbacks(3, quality=0.0)
        entries = opt._convert_route_feedback(fbs, decay_rate=0.9)
        for e in entries:
            assert e.confidence == 0.0

    def test_aggressive_decay(self):
        """decay_rate=0.1 → 最古はほぼ消失"""
        opt = PTOptimizer()
        fbs = _make_feedbacks(5, quality=1.0)
        entries = opt._convert_route_feedback(fbs, decay_rate=0.1)
        # 最古: 1.0 * 0.1^4 = 0.0001
        assert entries[0].confidence < 0.001
        assert entries[-1].confidence == 1.0


class TestRecencyDecayDefault:
    """デフォルト decay_rate=0.95"""

    def test_default_rate(self):
        """デフォルト decay_rate で呼び出し"""
        opt = PTOptimizer()
        fbs = _make_feedbacks(10, quality=0.8)
        entries = opt._convert_route_feedback(fbs)
        # 最新は 0.8、最古は 0.8 * 0.95^9 ≈ 0.505
        assert abs(entries[-1].confidence - 0.8) < 0.001
        assert entries[0].confidence < entries[-1].confidence
        assert entries[0].confidence > 0.4  # 0.95^9 ≈ 0.63, * 0.8 ≈ 0.505
