#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/symploke/tests/
# PURPOSE: F4 basanos_feedback.py のユニットテスト
"""Tests for Basanos Perspective Feedback system."""

import json
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from basanos_feedback import FeedbackStore, PerspectiveFeedback


# PURPOSE: PerspectiveFeedback dataclass tests
class TestPerspectiveFeedback:
    """PerspectiveFeedback dataclass tests."""

    # PURPOSE: 未使用 perspective は 0.5 (ニュートラル)。
    def test_default_usefulness_rate(self):
        """未使用 perspective は 0.5 (ニュートラル)。"""
        fb = PerspectiveFeedback(
            perspective_id="BP-Security-O1",
            domain="Security",
            axis="O1",
        )
        assert fb.usefulness_rate == 0.5

    # PURPOSE: 有用率の計算。
    def test_usefulness_rate_calculation(self):
        """有用率の計算。"""
        fb = PerspectiveFeedback(
            perspective_id="BP-Security-O1",
            domain="Security",
            axis="O1",
            total_reviews=10,
            useful_count=3,
        )
        assert fb.usefulness_rate == pytest.approx(0.3)

    # PURPOSE: 0 reviews = 0.5 (ゼロ除算回避)。
    def test_zero_reviews_returns_neutral(self):
        """0 reviews = 0.5 (ゼロ除算回避)。"""
        fb = PerspectiveFeedback(
            perspective_id="BP-Test-O1",
            domain="Test",
            axis="O1",
            total_reviews=0,
            useful_count=0,
        )
        assert fb.usefulness_rate == 0.5


# PURPOSE: FeedbackStore persistence and filtering tests
class TestFeedbackStore:
    """FeedbackStore persistence and filtering tests."""

    # PURPOSE: tmp_state_file の処理
    @pytest.fixture
    def tmp_state_file(self, tmp_path):
        return tmp_path / "test_feedback_state.json"

    # PURPOSE: 空の store — perspective なし。
    def test_empty_store(self, tmp_state_file):
        """空の store — perspective なし。"""
        store = FeedbackStore(state_file=tmp_state_file)
        assert store.get_all_feedback() == {}

    # PURPOSE: 記録と取得。
    def test_record_and_retrieve(self, tmp_state_file):
        """記録と取得。"""
        store = FeedbackStore(state_file=tmp_state_file)
        store.record_usage("BP-Security-O1", "Security", "O1", was_useful=True)
        store.record_usage("BP-Security-O1", "Security", "O1", was_useful=False)

        fb = store.get_all_feedback()
        assert "BP-Security-O1" in fb
        assert fb["BP-Security-O1"].total_reviews == 2
        assert fb["BP-Security-O1"].useful_count == 1

    # PURPOSE: 保存→再読込。
    def test_persistence(self, tmp_state_file):
        """保存→再読込。"""
        store1 = FeedbackStore(state_file=tmp_state_file)
        store1.record_usage("BP-Test-S2", "Test", "S2", was_useful=True)
        store1.save()

        store2 = FeedbackStore(state_file=tmp_state_file)
        fb = store2.get_all_feedback()
        assert "BP-Test-S2" in fb
        assert fb["BP-Test-S2"].useful_count == 1

    # PURPOSE: 低品質フィルタリング — 10回以上使用 + 有用率 < threshold。
    def test_low_quality_filter(self, tmp_state_file):
        """低品質フィルタリング — 10回以上使用 + 有用率 < threshold。"""
        store = FeedbackStore(state_file=tmp_state_file)
        # 低品質: 10回使用、0回有用
        for _ in range(10):
            store.record_usage("BP-Bad-O1", "Bad", "O1", was_useful=False)
        # 高品質: 10回使用、8回有用
        for i in range(10):
            store.record_usage("BP-Good-O2", "Good", "O2", was_useful=(i < 8))
        # 未使用: 3回のみ (閾値の10回に満たない)
        for _ in range(3):
            store.record_usage("BP-New-S1", "New", "S1", was_useful=False)

        low = store.get_low_quality_perspectives(threshold=0.1)
        assert "BP-Bad-O1" in low
        assert "BP-Good-O2" not in low
        assert "BP-New-S1" not in low  # 10回未満は除外

    # PURPOSE: 壊れたファイルは無視。
    def test_corrupted_file_ignored(self, tmp_state_file):
        """壊れたファイルは無視。"""
        tmp_state_file.write_text("invalid json")
        store = FeedbackStore(state_file=tmp_state_file)
        assert store.get_all_feedback() == {}


# PURPOSE: F5: Hybrid mode specialist selection tests
class TestHybridMode:
    """F5: Hybrid mode specialist selection tests."""

    # PURPOSE: Hybrid ratio で basanos / specialist の数が正しく分割される。
    def test_hybrid_ratio_split(self):
        """Hybrid ratio で basanos / specialist の数が正しく分割される。"""
        total = 20
        ratio = 0.6
        basanos_count = max(1, int(total * ratio))
        specialist_count = total - basanos_count
        assert basanos_count == 12
        assert specialist_count == 8
        assert basanos_count + specialist_count == total

    # PURPOSE: ratio=0.0 → basanos 最低1。
    def test_hybrid_ratio_edge_zero(self):
        """ratio=0.0 → basanos 最低1。"""
        total = 20
        ratio = 0.0
        basanos_count = max(1, int(total * ratio))
        specialist_count = total - basanos_count
        assert basanos_count == 1
        assert specialist_count == 19

    # PURPOSE: ratio=1.0 → basanos が全て。
    def test_hybrid_ratio_edge_one(self):
        """ratio=1.0 → basanos が全て。"""
        total = 20
        ratio = 1.0
        basanos_count = max(1, int(total * ratio))
        specialist_count = total - basanos_count
        assert basanos_count == 20
        assert specialist_count == 0
