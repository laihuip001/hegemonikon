#!/usr/bin/env python3
# PURPOSE: PKS v2 新コンポーネントのテスト
"""
PKS v2 テストスイート

対象:
- attractor_context: AttractorContextBridge, SERIES_TOPICS
- feedback: FeedbackCollector, PushFeedback
- pks_engine: auto_context_from_input, record_feedback
"""

import json
from pathlib import Path

import pytest

from mekhane.pks.attractor_context import (
    SERIES_TOPICS,
    SERIES_WORKFLOWS,
    AttractorContext,
    AttractorContextBridge,
)
from mekhane.pks.feedback import (
    REACTION_WEIGHTS,
    FeedbackCollector,
    PushFeedback,
)
from mekhane.pks.pks_engine import SessionContext


# =============================================================================
# AttractorContext (unit — no Attractor dependency)
# =============================================================================


# PURPOSE: Test series topics mapping の実装
class TestSeriesTopicsMapping:
    # PURPOSE: all_6_series_defined をテストする
    def test_all_6_series_defined(self):
        assert set(SERIES_TOPICS.keys()) == {"O", "S", "H", "P", "K", "A"}

    # PURPOSE: all_6_workflow_sets をテストする
    def test_all_6_workflow_sets(self):
        assert set(SERIES_WORKFLOWS.keys()) == {"O", "S", "H", "P", "K", "A"}

    # PURPOSE: topics_non_empty をテストする
    def test_topics_non_empty(self):
        for series, topics in SERIES_TOPICS.items():
            assert len(topics) >= 3, f"{series} has too few topics"

    # PURPOSE: workflows_non_empty をテストする
    def test_workflows_non_empty(self):
        for series, workflows in SERIES_WORKFLOWS.items():
            assert len(workflows) >= 2, f"{series} has too few workflows"


# PURPOSE: Test attractor context bridge の実装
class TestAttractorContextBridge:
    # PURPOSE: to_session_context_basic をテストする
    def test_to_session_context_basic(self):
        bridge = AttractorContextBridge()
        ctx = AttractorContext(
            series="K",
            similarity=0.75,
            oscillation="clear",
            topics=["調査", "論文", "知識"],
            workflows=["/sop", "/epi"],
        )
        session = bridge.to_session_context(ctx)
        assert "調査" in session.topics
        assert "/sop" in session.active_workflows

    # PURPOSE: to_session_context_oscillation_merges_topics をテストする
    def test_to_session_context_oscillation_merges_topics(self):
        bridge = AttractorContextBridge()
        ctx = AttractorContext(
            series="K",
            similarity=0.55,
            oscillation="positive",
            topics=["調査", "論文"],
            workflows=["/sop"],
            secondary_series="A",
            secondary_topics=["評価", "判断"],
        )
        session = bridge.to_session_context(ctx)
        # Both K and A topics merged
        assert "調査" in session.topics
        assert "評価" in session.topics
        assert "判断" in session.topics

    # PURPOSE: to_session_context_no_duplicates をテストする
    def test_to_session_context_no_duplicates(self):
        bridge = AttractorContextBridge()
        ctx = AttractorContext(
            series="O",
            similarity=0.5,
            oscillation="positive",
            topics=["認識", "FEP"],
            workflows=["/noe"],
            secondary_series="O",
            secondary_topics=["認識", "FEP"],  # same
        )
        session = bridge.to_session_context(ctx)
        assert session.topics.count("認識") == 1


# PURPOSE: Attractor 依存のテスト — GPU/モデル必要
class TestAttractorContextBridgeIntegration:
    """Attractor 依存のテスト — GPU/モデル必要"""

    # PURPOSE: bridge の処理
    @pytest.fixture
    def bridge(self):
        try:
            b = AttractorContextBridge(force_cpu=True)
            b._get_attractor()  # force init
            return b
        except Exception:
            pytest.skip("Attractor not available")

    # PURPOSE: infer_context_returns_series をテストする
    def test_infer_context_returns_series(self, bridge):
        ctx = bridge.infer_context("アーキテクチャを設計する")
        assert ctx.series in ("O", "S", "H", "P", "K", "A")
        assert ctx.similarity > 0
        assert ctx.oscillation in ("clear", "positive", "negative")

    # PURPOSE: infer_session_context_e2e をテストする
    def test_infer_session_context_e2e(self, bridge):
        session = bridge.infer_session_context("調査して論文を読む")
        assert isinstance(session, SessionContext)
        assert len(session.topics) > 0


# =============================================================================
# FeedbackCollector
# =============================================================================


# PURPOSE: Test push feedback の実装
class TestPushFeedback:
    # PURPOSE: auto_timestamp をテストする
    def test_auto_timestamp(self):
        fb = PushFeedback(
            nugget_title="test", reaction="used", series="K"
        )
        assert fb.timestamp != ""

    # PURPOSE: explicit_timestamp をテストする
    def test_explicit_timestamp(self):
        fb = PushFeedback(
            nugget_title="test",
            reaction="used",
            series="K",
            timestamp="2026-01-01T00:00:00",
        )
        assert fb.timestamp == "2026-01-01T00:00:00"


# PURPOSE: Test feedback collector の実装
class TestFeedbackCollector:
    # PURPOSE: record_and_stats をテストする
    def test_record_and_stats(self):
        collector = FeedbackCollector(persist_path=Path("/tmp/test_fb.json"))
        collector.record(PushFeedback("paper1", "used", "K"))
        collector.record(PushFeedback("paper2", "dismissed", "K"))

        stats = collector.get_stats()
        assert "K" in stats
        assert stats["K"]["count"] == 2

    # PURPOSE: adjust_threshold_positive_feedback をテストする
    def test_adjust_threshold_positive_feedback(self):
        collector = FeedbackCollector(persist_path=Path("/tmp/test_fb2.json"))
        # All positive → threshold should decrease
        for i in range(5):
            collector.record(PushFeedback(f"paper{i}", "used", "S"))

        threshold = collector.adjust_threshold("S", base_threshold=0.65)
        assert threshold < 0.65  # positive feedback lowers threshold

    # PURPOSE: adjust_threshold_negative_feedback をテストする
    def test_adjust_threshold_negative_feedback(self):
        collector = FeedbackCollector(persist_path=Path("/tmp/test_fb3.json"))
        # All negative → threshold should increase
        for i in range(5):
            collector.record(PushFeedback(f"paper{i}", "dismissed", "H"))

        threshold = collector.adjust_threshold("H", base_threshold=0.65)
        assert threshold > 0.65  # negative feedback raises threshold

    # PURPOSE: adjust_threshold_no_data をテストする
    def test_adjust_threshold_no_data(self):
        collector = FeedbackCollector(persist_path=Path("/tmp/test_fb4.json"))
        # No data → base threshold
        threshold = collector.adjust_threshold("X", base_threshold=0.65)
        assert threshold == 0.65

    # PURPOSE: adjust_threshold_clamped をテストする
    def test_adjust_threshold_clamped(self):
        collector = FeedbackCollector(persist_path=Path("/tmp/test_fb5.json"))
        # Extreme positive
        for i in range(100):
            collector.record(PushFeedback(f"p{i}", "deepened", "A"))
        threshold = collector.adjust_threshold("A")
        assert threshold >= 0.3  # clamped

    # PURPOSE: persist_and_reload をテストする
    def test_persist_and_reload(self, tmp_path):
        fb_path = tmp_path / "feedback.json"
        collector = FeedbackCollector(persist_path=fb_path)
        collector.record(PushFeedback("paper1", "used", "K"))
        collector.persist()
        assert fb_path.exists()

        # Reload
        collector2 = FeedbackCollector(persist_path=fb_path)
        stats = collector2.get_stats()
        assert stats["K"]["count"] == 1

    # PURPOSE: reaction_weights_defined をテストする
    def test_reaction_weights_defined(self):
        assert "used" in REACTION_WEIGHTS
        assert "dismissed" in REACTION_WEIGHTS
        assert "deepened" in REACTION_WEIGHTS
        assert "ignored" in REACTION_WEIGHTS
        assert REACTION_WEIGHTS["deepened"] > REACTION_WEIGHTS["used"]
