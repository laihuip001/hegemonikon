#!/usr/bin/env python3
# PURPOSE: PKS v2 E2E シナリオテスト
"""
PKS v2 End-to-End シナリオテスト

テスト対象フロー:
1. Input → Attractor → Context → Push (auto_context_from_input 全体)
2. Feedback → Threshold 変動 → 次回 Push が変わる
3. SyncWatcher → on_change → Push callback
4. Narrator LLM fallback → テンプレート生成
5. MatrixView fallback → メタデータ比較表
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mekhane.pks.attractor_context import (
    AttractorContext,
    AttractorContextBridge,
)
from mekhane.pks.feedback import FeedbackCollector, PushFeedback
from mekhane.pks.narrator import PKSNarrator
from mekhane.pks.matrix_view import PKSMatrixView
from mekhane.pks.pks_engine import (
    KnowledgeNugget,
    PKSEngine,
    SessionContext,
)
from mekhane.pks.sync_watcher import FileChange, SyncWatcher


# =============================================================================
# Helper: テスト用 nugget 生成
# =============================================================================

def _make_nugget(
    title: str = "Test Paper",
    source: str = "test",
    score: float = 0.75,
    abstract: str = "テスト要約",
) -> KnowledgeNugget:
    return KnowledgeNugget(
        title=title,
        source=source,
        relevance_score=score,
        abstract=abstract,
        push_reason="Test reason",
    )


# =============================================================================
# Scenario 1: Context → Push フロー全体
# =============================================================================


# PURPOSE: Attractor → Context → Engine の完全フロー
class TestScenario1_ContextPush:
    """Input → Attractor → Context → Push の統合テスト"""

    def test_attractor_bridge_sets_engine_context(self):
        """AttractorContextBridge がエンジンのトピック/WFを設定できる"""
        engine = PKSEngine(
            enable_questions=False,
            enable_serendipity=False,
            enable_feedback=False,
        )

        # Attractor Bridge を直接使用
        bridge = AttractorContextBridge()
        ctx = AttractorContext(
            series="K",
            similarity=0.8,
            oscillation="clear",
            topics=["調査", "論文", "知識"],
            workflows=["/sop", "/epi"],
        )
        session = bridge.to_session_context(ctx)

        # エンジンに設定
        engine.set_context(
            topics=session.topics,
            workflows=session.active_workflows,
        )

        assert "調査" in engine.tracker.context.topics
        assert "/sop" in engine.tracker.context.active_workflows

    def test_context_produces_embedding_text(self):
        """コンテキストが有効な embedding テキストを生成する"""
        engine = PKSEngine(
            enable_questions=False,
            enable_serendipity=False,
            enable_feedback=False,
        )
        engine.set_context(topics=["FEP", "Active Inference"])

        text = engine.tracker.context.to_embedding_text()
        assert "FEP" in text
        assert "Active Inference" in text
        assert text != "general knowledge"


# =============================================================================
# Scenario 2: Feedback → Threshold 調整ループ
# =============================================================================


# PURPOSE: Feedback → Threshold 変動の完全ループ
class TestScenario2_FeedbackLoop:
    """Feedback → Threshold 変動 → 次回 Push に反映"""

    def test_positive_feedback_lowers_threshold_for_series(self, tmp_path):
        """正のフィードバックが閾値を下げる (より多く push)"""
        fb_path = tmp_path / "s2_feedback.json"
        collector = FeedbackCollector(persist_path=fb_path)

        # S series で連続 positive
        for i in range(5):
            collector.record(PushFeedback(f"paper_{i}", "used", "S"))

        base = 0.65
        adjusted = collector.adjust_threshold("S", base)
        assert adjusted < base, f"Expected < {base}, got {adjusted}"

        # persist → reload → 同じ結果
        collector.persist()
        collector2 = FeedbackCollector(persist_path=fb_path)
        adjusted2 = collector2.adjust_threshold("S", base)
        assert adjusted2 == adjusted, "Reloaded threshold should match"

    def test_negative_feedback_raises_threshold_for_series(self, tmp_path):
        """負のフィードバックが閾値を上げる (push を抑制)"""
        fb_path = tmp_path / "s2_feedback_neg.json"
        collector = FeedbackCollector(persist_path=fb_path)

        for i in range(5):
            collector.record(PushFeedback(f"paper_{i}", "dismissed", "H"))

        adjusted = collector.adjust_threshold("H", 0.65)
        assert adjusted > 0.65

    def test_mixed_feedback_converges(self, tmp_path):
        """混合フィードバックは微調整に収束する"""
        fb_path = tmp_path / "s2_feedback_mix.json"
        collector = FeedbackCollector(persist_path=fb_path)

        # 3 positive, 2 negative → net slightly positive
        for i in range(3):
            collector.record(PushFeedback(f"good_{i}", "used", "O"))
        for i in range(2):
            collector.record(PushFeedback(f"bad_{i}", "dismissed", "O"))

        adjusted = collector.adjust_threshold("O", 0.65)
        # Net positive → slightly lower
        assert abs(adjusted - 0.65) < 0.15, "Mixed feedback should converge near base"

    def test_feedback_independence_across_series(self, tmp_path):
        """異なる series の feedback は互いに影響しない"""
        fb_path = tmp_path / "s2_feedback_ind.json"
        collector = FeedbackCollector(persist_path=fb_path)

        # K: all positive, H: all negative
        for i in range(5):
            collector.record(PushFeedback(f"k_{i}", "used", "K"))
            collector.record(PushFeedback(f"h_{i}", "dismissed", "H"))

        k_threshold = collector.adjust_threshold("K", 0.65)
        h_threshold = collector.adjust_threshold("H", 0.65)

        assert k_threshold < 0.65, "K should be lower (positive)"
        assert h_threshold > 0.65, "H should be higher (negative)"
        assert k_threshold != h_threshold, "Different series, different thresholds"

    def test_engine_record_feedback_persists(self, tmp_path):
        """PKSEngine.record_feedback が FeedbackCollector に記録される"""
        engine = PKSEngine(
            enable_questions=False,
            enable_serendipity=False,
            enable_feedback=True,
        )
        # feedback collector のパスを上書き
        if engine._feedback:
            engine._feedback._path = tmp_path / "engine_fb.json"

        engine.record_feedback("test_paper", "deepened", "A")

        if engine._feedback:
            stats = engine._feedback.get_stats()
            assert "A" in stats
            assert stats["A"]["count"] == 1


# =============================================================================
# Scenario 3: SyncWatcher callback → Push
# =============================================================================


# PURPOSE: SyncWatcher が変更を検知して callback を発火する
class TestScenario3_SyncWatcherCallback:
    """SyncWatcher on_change → Push callback の統合テスト"""

    def test_on_change_callback_fires_on_changes(self, tmp_path):
        """ファイル変更時に callback が呼ばれる"""
        callback_called = []

        def mock_callback(changes):
            callback_called.append(changes)

        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        watcher = SyncWatcher(
            watch_dirs=[watch_dir],
            extensions=(".md",),
            state_dir=tmp_path,
            on_change=mock_callback,
        )

        # ファイル作成
        (watch_dir / "test.md").write_text("# Test")

        # run_once → callback fire
        changes = watcher.run_once()
        assert len(changes) > 0
        assert len(callback_called) == 1

    def test_on_change_not_called_when_no_changes(self, tmp_path):
        """変更がなければ callback は呼ばれない"""
        callback_called = []

        def mock_callback(changes):
            callback_called.append(changes)

        watch_dir = tmp_path / "watch2"
        watch_dir.mkdir()

        watcher = SyncWatcher(
            watch_dirs=[watch_dir],
            extensions=(".md",),
            state_dir=tmp_path,
            on_change=mock_callback,
        )

        # 初回: 何もなし
        watcher.run_once()
        assert len(callback_called) == 0

    def test_create_push_callback_returns_callable(self):
        """create_push_callback がコーラブルを返す"""
        callback = SyncWatcher.create_push_callback(topics=["FEP"])
        assert callable(callback)

    def test_callback_error_does_not_crash_watcher(self, tmp_path):
        """callback がエラーを起こしても watcher は止まらない"""
        def bad_callback(changes):
            raise RuntimeError("Intentional error")

        watch_dir = tmp_path / "watch3"
        watch_dir.mkdir()

        watcher = SyncWatcher(
            watch_dirs=[watch_dir],
            extensions=(".md",),
            state_dir=tmp_path,
            on_change=bad_callback,
        )

        (watch_dir / "test.md").write_text("# Test")

        # Should not raise
        changes = watcher.run_once()
        assert len(changes) > 0  # Changes still detected


# =============================================================================
# Scenario 4: Narrator fallback
# =============================================================================


# PURPOSE: Narrator の LLM → テンプレートフォールバック
class TestScenario4_NarratorFallback:
    """Narrator の LLM フォールバック動作"""

    def test_narrator_without_llm_uses_template(self):
        """LLM なし → テンプレート生成"""
        narrator = PKSNarrator(use_llm=False)
        assert not narrator.llm_available

        nugget = _make_nugget()
        narrative = narrator.narrate(nugget)
        assert len(narrative.segments) == 3
        assert narrative.segments[0].speaker == "Advocate"
        assert narrative.segments[1].speaker == "Critic"

    def test_narrator_batch_consistency(self):
        """バッチ処理で各 nugget が独立にナラレート"""
        narrator = PKSNarrator(use_llm=False)
        nuggets = [
            _make_nugget(title="Paper A", score=0.9),
            _make_nugget(title="Paper B", score=0.5),
        ]
        narratives = narrator.narrate_batch(nuggets)
        assert len(narratives) == 2
        assert narratives[0].title == "Paper A"
        assert narratives[1].title == "Paper B"

    def test_narrator_report_format(self):
        """レポートフォーマットが正しい Markdown"""
        narrator = PKSNarrator(use_llm=False)
        nuggets = [_make_nugget()]
        narratives = narrator.narrate_batch(nuggets)
        report = narrator.format_report(narratives)
        assert "# 🎙️ PKS Narrative Report" in report
        assert "Advocate" in report
        assert "Critic" in report

    def test_llm_parse_response_valid(self):
        """LLM レスポンスの正常パース"""
        narrator = PKSNarrator(use_llm=False)
        text = "ADVOCATE: この研究は重要です。\nCRITIC: しかし限界があります。\nADVOCATE: その通りですが参考になります。"
        result = narrator._parse_llm_response(text, _make_nugget())
        assert result is not None
        assert len(result.segments) == 3

    def test_llm_parse_response_invalid(self):
        """不正な LLM レスポンス → None (テンプレートにフォールバック)"""
        narrator = PKSNarrator(use_llm=False)
        text = "This is not in the expected format at all."
        result = narrator._parse_llm_response(text, _make_nugget())
        assert result is None


# =============================================================================
# Scenario 5: MatrixView fallback
# =============================================================================


# PURPOSE: MatrixView の LLM → メタデータフォールバック
class TestScenario5_MatrixViewFallback:
    """MatrixView の LLM フォールバック動作"""

    def test_matrix_without_llm(self):
        """LLM なし → Phase 1 メタデータ比較表"""
        view = PKSMatrixView(use_llm=False)
        assert not view.llm_available

        nuggets = [
            _make_nugget(title="Paper A"),
            _make_nugget(title="Paper B"),
        ]
        result = view.generate(nuggets)
        assert "## 📊 PKS Matrix View" in result
        assert "Paper A" in result
        assert "Paper B" in result

    def test_generate_with_llm_falls_back(self):
        """LLM 不可 → generate_with_llm が Phase 1 にフォールバック"""
        view = PKSMatrixView(use_llm=False)
        nuggets = [_make_nugget()]
        result = view.generate_with_llm(nuggets)
        assert "📊 PKS Matrix View" in result

    def test_matrix_empty_nuggets(self):
        """空リスト → 空メッセージ"""
        view = PKSMatrixView(use_llm=False)
        assert view.generate([]) == "📭 比較対象なし"
        assert view.generate_with_llm([]) == "📭 比較対象なし"

    def test_matrix_pipe_escape(self):
        """パイプ文字がエスケープされる"""
        view = PKSMatrixView(use_llm=False)
        nugget = _make_nugget(title="A | B")
        result = view.generate([nugget])
        assert "A \\| B" in result


# =============================================================================
# Scenario 6: 統合 — Context → Feedback → Threshold の完全ループ
# =============================================================================


# PURPOSE: コンテキスト設定〜フィードバック〜閾値調整の完全サイクル
class TestScenario6_FullLoop:
    """最も重要: 全コンポーネントを横断するサイクルテスト"""

    def test_context_feedback_threshold_cycle(self, tmp_path):
        """Context設定 → (mock) Push → Feedback → 閾値変動 の完全サイクル"""
        fb_path = tmp_path / "cycle_fb.json"

        engine = PKSEngine(
            threshold=0.65,
            enable_questions=False,
            enable_serendipity=False,
            enable_feedback=True,
        )
        engine._feedback._path = fb_path

        # 1. コンテキスト設定 (Attractor Bridge 経由をシミュレート)
        engine.set_context(topics=["FEP", "Active Inference"])
        assert "FEP" in engine.tracker.context.topics

        # 2. base threshold 確認
        assert engine._base_threshold == 0.65
        assert engine.detector.threshold == 0.65

        # 3. positive feedback を記録
        engine.record_feedback("FEP paper", "used", "O")
        engine.record_feedback("AI paper", "deepened", "O")

        # 4. 次回の auto_context_from_input をシミュレート
        #    (Attractor は使わず、feedback 調整だけ確認)
        if engine._feedback:
            adjusted = engine._feedback.adjust_threshold("O", engine._base_threshold)
            engine.detector.threshold = adjusted

        # 5. 閾値が下がったことを確認 (positive feedback)
        assert engine.detector.threshold < 0.65, (
            f"Expected threshold < 0.65 after positive feedback, "
            f"got {engine.detector.threshold}"
        )

    def test_multi_series_independent_thresholds(self, tmp_path):
        """複数 series の独立した閾値調整"""
        fb_path = tmp_path / "multi_fb.json"

        engine = PKSEngine(
            threshold=0.65,
            enable_questions=False,
            enable_serendipity=False,
            enable_feedback=True,
        )
        engine._feedback._path = fb_path

        # K series: positive
        for i in range(3):
            engine.record_feedback(f"k_paper_{i}", "used", "K")

        # H series: negative
        for i in range(3):
            engine.record_feedback(f"h_paper_{i}", "dismissed", "H")

        k_adj = engine._feedback.adjust_threshold("K", 0.65)
        h_adj = engine._feedback.adjust_threshold("H", 0.65)

        assert k_adj < 0.65, "K should be lower"
        assert h_adj > 0.65, "H should be higher"
        assert k_adj < h_adj, "K < H"
