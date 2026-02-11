"""
Tests for Timeline, Kalon, and Symploke Mnēmē API routes.
"""

import pytest
from unittest.mock import patch

# --- Timeline Tests ---


class TestTimelineRouter:
    """Timeline API テスト"""

    def test_import(self):
        """timeline ルーターがインポートできる"""
        from mekhane.api.routes.timeline import router
        assert router is not None

    def test_file_id(self):
        """_file_id が安定した短い ID を生成"""
        from pathlib import Path
        from mekhane.api.routes.timeline import _file_id
        p = Path("/tmp/test_file.md")
        fid = _file_id(p)
        assert isinstance(fid, str)
        assert len(fid) > 0
        # 同じパスは同じ ID
        assert _file_id(p) == fid

    def test_extract_date_iso(self):
        """ISO形式の日付を抽出"""
        from mekhane.api.routes.timeline import _extract_date
        result = _extract_date("handoff_2026-02-11_1444.md")
        assert result is not None
        assert "2026" in result

    def test_extract_title(self):
        """Markdown タイトル抽出"""
        from mekhane.api.routes.timeline import _extract_title
        title = _extract_title("# My Title\n\nBody text", "fallback.md")
        assert title == "My Title"

    def test_extract_title_fallback(self):
        """タイトルなしの場合ファイル名にフォールバック"""
        from mekhane.api.routes.timeline import _extract_title
        title = _extract_title("No heading here", "fallback.md")
        assert title == "fallback"

    def test_extract_summary(self):
        """サマリー抽出"""
        from mekhane.api.routes.timeline import _extract_summary
        content = "# Title\n\n> Quote\n\nThis is the summary paragraph."
        summary = _extract_summary(content)
        assert "summary" in summary.lower() or len(summary) > 0

    def test_scan_events_returns_list(self):
        """_scan_events がリストを返す"""
        from mekhane.api.routes.timeline import _scan_events
        events = _scan_events()
        assert isinstance(events, list)

    def test_scan_events_with_filter(self):
        """イベントタイプでフィルタ"""
        from mekhane.api.routes.timeline import _scan_events
        events = _scan_events(event_type="handoff")
        assert isinstance(events, list)
        # フィルタされた結果は全て handoff タイプ
        for e in events:
            assert e.get("type") == "handoff"


# --- Kalon Tests ---


class TestKalonRouter:
    """Kalon API テスト"""

    def test_import(self):
        """kalon ルーターがインポートできる"""
        from mekhane.api.routes.kalon import router
        assert router is not None

    def test_verdict_kalon(self):
        """G=True, F=True → ◎ (kalon)"""
        from mekhane.api.routes.kalon import _verdict
        assert _verdict(True, True) == "◎"

    def test_verdict_acceptable(self):
        """G=False, F=True → ◯"""
        from mekhane.api.routes.kalon import _verdict
        assert _verdict(False, True) == "◯"

    def test_verdict_trivial(self):
        """G=True, F=False → ✗"""
        from mekhane.api.routes.kalon import _verdict
        assert _verdict(True, False) == "✗"

    def test_verdict_distill(self):
        """G=False, F=False → ✗"""
        from mekhane.api.routes.kalon import _verdict
        assert _verdict(False, False) == "✗"

    def test_verdict_label(self):
        """ラベル生成"""
        from mekhane.api.routes.kalon import _verdict_label
        label = _verdict_label(True, True)
        assert "kalon" in label.lower() or "Fix" in label


# --- Symploke Mnēmē Integration Tests ---


class TestSymplokeMnemeIntegration:
    """Symploke Mnēmē SearchEngine 統合テスト"""

    def test_gnosis_index_import(self):
        """GnosisIndex がインポートできる"""
        from mekhane.symploke.indices import GnosisIndex
        assert GnosisIndex is not None

    def test_chronos_index_import(self):
        """ChronosIndex がインポートできる"""
        from mekhane.symploke.indices import ChronosIndex
        assert ChronosIndex is not None

    def test_search_engine_import(self):
        """SearchEngine がインポートできる"""
        from mekhane.symploke.search.engine import SearchEngine
        engine = SearchEngine()
        assert engine is not None

    def test_source_type_values(self):
        """SourceType に gnosis と chronos が存在"""
        from mekhane.symploke.indices import SourceType
        assert hasattr(SourceType, "GNOSIS")
        assert hasattr(SourceType, "CHRONOS")


# --- SemanticAgent Export Tests ---


class TestSemanticAgentExport:
    """SemanticAgent エクスポートテスト"""

    def test_import_from_dokimasia(self):
        """dokimasia パッケージからインポートできる"""
        from mekhane.synteleia.dokimasia import SemanticAgent
        assert SemanticAgent is not None

    def test_import_from_synteleia(self):
        """synteleia トップレベルからインポートできる"""
        from mekhane.synteleia import SemanticAgent
        assert SemanticAgent is not None

    def test_in_all(self):
        """__all__ に含まれる"""
        import mekhane.synteleia as syn
        assert "SemanticAgent" in syn.__all__

    def test_with_l2_import(self):
        """with_l2 ファクトリが使える"""
        from mekhane.synteleia import SynteleiaOrchestrator
        orch = SynteleiaOrchestrator.with_l2()
        agent_names = [a.name for a in orch.agents]
        assert "SemanticAgent" in agent_names
