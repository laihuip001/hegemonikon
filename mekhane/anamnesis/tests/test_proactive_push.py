"""Proactive Push + Link Graph のテスト."""

import json
import re
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mekhane.anamnesis.proactive_push import (
    ProactivePush,
    Recommendation,
    PushResult,
    boot_push,
    context_push,
)
from mekhane.anamnesis.link_graph import (
    LinkGraph,
    GraphNode,
    build_knowledge_graph,
    load_or_build_graph,
)


# ==========================================================
# Proactive Push Tests
# ==========================================================


class TestRecommendation:
    """Recommendation dataclass のテスト."""

    def test_create(self):
        rec = Recommendation(
            title="Test Paper",
            source_type="papers",
            relevance=0.85,
            trigger="context",
            benefit="テスト用ベネフィット",
            content_snippet="テスト内容",
        )
        assert rec.title == "Test Paper"
        assert rec.relevance == 0.85
        assert "/eat" in rec.actions

    def test_default_actions(self):
        rec = Recommendation(
            title="t",
            source_type="papers",
            relevance=0.5,
            trigger="context",
            benefit="b",
            content_snippet="c",
        )
        assert rec.actions == ["/eat", "/jukudoku"]


class TestPushResult:
    """PushResult dataclass のテスト."""

    def test_empty(self):
        result = PushResult(
            recommendations=[],
            trigger_type="boot",
            query_used="test",
            retrieval_time=0.1,
            total_candidates=0,
        )
        assert len(result.recommendations) == 0

    def test_with_recommendations(self):
        rec = Recommendation(
            title="Paper 1",
            source_type="papers",
            relevance=0.9,
            trigger="context",
            benefit="b",
            content_snippet="c",
        )
        result = PushResult(
            recommendations=[rec],
            trigger_type="boot",
            query_used="test",
            retrieval_time=0.1,
            total_candidates=5,
        )
        assert len(result.recommendations) == 1


class TestProactivePush:
    """ProactivePush コアロジックのテスト."""

    def test_init(self):
        push = ProactivePush()
        assert push.max_recommendations == 3
        assert push.use_reranker is True

    def test_generate_benefit_papers(self):
        push = ProactivePush()
        result = {"title": "FEP Theory", "source": "papers", "_distance": 0.2}
        benefit = push._generate_benefit(result, "FEP")
        assert "FEP Theory" in benefit
        assert "80%" in benefit

    def test_generate_benefit_handoff(self):
        push = ProactivePush()
        result = {"title": "Session 42", "source": "handoff", "_distance": 0.3}
        benefit = push._generate_benefit(result, "query")
        assert "引継書" in benefit

    def test_to_recommendation(self):
        push = ProactivePush()
        result = {
            "title": "Test Paper",
            "_source_table": "papers",
            "source": "arxiv",
            "_distance": 0.3,
            "abstract": "This is the abstract.",
            "url": "http://example.com",
            "primary_key": "pk_001",
        }
        rec = push._to_recommendation(result, "query", trigger="context")
        assert rec.title == "Test Paper"
        assert rec.relevance == 0.7
        assert rec.trigger == "context"

    def test_to_recommendation_knowledge(self):
        push = ProactivePush()
        result = {
            "title": "KI Item",
            "_source_table": "knowledge",
            "source": "ki",
            "_distance": 0.4,
            "content": "知識項目の内容です。",
            "abstract": "要約",
        }
        rec = push._to_recommendation(result, "query", trigger="context")
        assert rec.content_snippet == "知識項目の内容です。"

    def test_deduplicate(self):
        push = ProactivePush()
        recs = [
            Recommendation(
                title="Paper A",
                source_type="papers",
                relevance=0.9,
                trigger="context",
                benefit="b",
                content_snippet="c",
                primary_key="pk_001",
            ),
            Recommendation(
                title="Paper A",
                source_type="papers",
                relevance=0.85,
                trigger="context",
                benefit="b",
                content_snippet="c",
                primary_key="pk_001",
            ),
        ]
        unique = push._deduplicate(recs)
        assert len(unique) == 1

    def test_reset_session(self):
        push = ProactivePush()
        push._seen_keys.add("test_key")
        push.reset_session()
        assert len(push._seen_keys) == 0

    def test_short_message_skipped(self):
        push = ProactivePush()
        with patch.object(push, "_retrieve", return_value=[]):
            result = push.context_recommendations("hi")
        assert len(result.recommendations) == 0

    @patch("mekhane.anamnesis.proactive_push.ProactivePush._retrieve")
    def test_context_recommendations(self, mock_retrieve):
        mock_retrieve.return_value = [
            {
                "title": "FEP and Active Inference",
                "_source_table": "papers",
                "source": "arxiv",
                "_distance": 0.3,
                "abstract": "Free energy principle...",
                "url": "http://arxiv.org/xxx",
                "primary_key": "pk_123",
            }
        ]

        push = ProactivePush()
        result = push.context_recommendations(
            "自由エネルギー原理の数学的定式化について教えて"
        )
        assert len(result.recommendations) == 1
        assert result.trigger_type == "context"
        assert result.recommendations[0].title == "FEP and Active Inference"

    def test_format_recommendations_empty(self):
        result = PushResult(
            recommendations=[],
            trigger_type="boot",
            query_used="test",
            retrieval_time=0,
            total_candidates=0,
        )
        formatted = ProactivePush.format_recommendations(result)
        assert formatted == ""

    def test_format_recommendations(self):
        rec = Recommendation(
            title="Test Paper",
            source_type="papers",
            relevance=0.85,
            trigger="context",
            benefit="テスト用ベネフィット",
            content_snippet="テスト内容の概要です",
        )
        result = PushResult(
            recommendations=[rec],
            trigger_type="boot",
            query_used="test",
            retrieval_time=0.5,
            total_candidates=10,
        )
        formatted = ProactivePush.format_recommendations(result)
        assert "語りかけています" in formatted
        assert "Test Paper" in formatted

    def test_format_compact(self):
        rec = Recommendation(
            title="Test",
            source_type="papers",
            relevance=0.9,
            trigger="context",
            benefit="b",
            content_snippet="c",
        )
        result = PushResult(
            recommendations=[rec],
            trigger_type="context",
            query_used="q",
            retrieval_time=0.1,
            total_candidates=1,
        )
        formatted = ProactivePush.format_compact(result)
        assert "関連知識" in formatted

    @patch("mekhane.anamnesis.proactive_push.ProactivePush._graph_recommendations")
    @patch("mekhane.anamnesis.proactive_push.ProactivePush._extract_latest_context")
    @patch("mekhane.anamnesis.proactive_push.ProactivePush._retrieve")
    def test_boot_recommendations(self, mock_retrieve, mock_context, mock_graph):
        mock_context.return_value = "セッション管理と記憶検索"
        mock_retrieve.return_value = [
            {
                "title": "Memory Enhancement",
                "_source_table": "knowledge",
                "source": "session",
                "_distance": 0.4,
                "content": "記憶検索の強化...",
                "primary_key": "session:mem:0",
            }
        ]
        mock_graph.return_value = []  # Graph 推薦なし

        push = ProactivePush()
        result = push.boot_recommendations()
        assert result.trigger_type == "boot"
        assert len(result.recommendations) == 1

    @patch("mekhane.anamnesis.proactive_push.ProactivePush._graph_recommendations")
    @patch("mekhane.anamnesis.proactive_push.ProactivePush._extract_latest_context")
    @patch("mekhane.anamnesis.proactive_push.ProactivePush._retrieve")
    def test_boot_with_graph_recommendations(self, mock_retrieve, mock_context, mock_graph):
        """Context-Triggered + Graph-Triggered の統合テスト."""
        mock_context.return_value = "認知アーキテクチャ"
        mock_retrieve.return_value = [
            {
                "title": "Context Paper",
                "_source_table": "papers",
                "source": "arxiv",
                "_distance": 0.3,
                "abstract": "ベクトル近傍の論文",
                "primary_key": "ctx_001",
            }
        ]
        mock_graph.return_value = [
            Recommendation(
                title="Bridge Node",
                source_type="kernel",
                relevance=0.7,
                trigger="bridge",
                benefit="ブリッジノード推薦",
                content_snippet="グラフ上の構造的関連",
                primary_key="bridge_001",
            )
        ]

        push = ProactivePush()
        result = push.boot_recommendations()
        assert result.trigger_type == "boot"
        assert len(result.recommendations) == 2
        triggers = {r.trigger for r in result.recommendations}
        assert "context" in triggers
        assert "bridge" in triggers
        assert result.total_candidates == 2  # 1 context + 1 graph

    def test_boot_no_context(self):
        push = ProactivePush()
        with patch.object(push, "_extract_latest_context", return_value=""):
            result = push.boot_recommendations()
        assert len(result.recommendations) == 0


# ==========================================================
# Link Graph Tests
# ==========================================================


class TestLinkGraph:
    """LinkGraph のテスト."""

    def _create_test_vault(self, tmp_path: Path) -> Path:
        """テスト用の Markdown ファイル群を作成."""
        vault = tmp_path / "vault"
        vault.mkdir()

        (vault / "note_a.md").write_text(
            "# Note A\n\nThis links to [[note_b]] and [[note_c]].\n"
        )
        (vault / "note_b.md").write_text(
            "# Note B\n\nReference to [Note A](note_a.md).\n"
        )
        (vault / "note_c.md").write_text(
            "# Note C\n\nSee: [[note_a]]\nAlso see: [[note_b]]\n"
        )
        (vault / "orphan.md").write_text("# Orphan\n\nNo links here.\n")
        return vault

    def test_scan_directory(self, tmp_path):
        vault = self._create_test_vault(tmp_path)
        graph = LinkGraph()
        count = graph.scan_directory(vault)
        assert count == 4

    def test_wikilink_extraction(self, tmp_path):
        vault = self._create_test_vault(tmp_path)
        graph = LinkGraph()
        graph.scan_directory(vault)

        note_a = graph.nodes["note_a"]
        assert "note_b" in note_a.out_links
        assert "note_c" in note_a.out_links

    def test_backlinks(self, tmp_path):
        vault = self._create_test_vault(tmp_path)
        graph = LinkGraph()
        graph.scan_directory(vault)

        # note_a は note_b と note_c からリンクされている
        backlinks = graph.get_backlinks("note_a")
        assert "note_b" in backlinks
        assert "note_c" in backlinks

    def test_bidirectional(self, tmp_path):
        vault = self._create_test_vault(tmp_path)
        graph = LinkGraph()
        graph.scan_directory(vault)

        # note_a → note_b (forward)
        assert "note_b" in graph.nodes["note_a"].out_links
        # note_b → note_a (forward via markdown link)
        assert "note_a" in graph.nodes["note_b"].out_links
        # note_a ← note_b (backlink)
        assert "note_b" in graph.nodes["note_a"].in_links

    def test_neighbors(self, tmp_path):
        vault = self._create_test_vault(tmp_path)
        graph = LinkGraph()
        graph.scan_directory(vault)

        neighbors = graph.get_neighbors("note_a", hops=1)
        assert "note_b" in neighbors
        assert "note_c" in neighbors

    def test_neighbors_2_hops(self, tmp_path):
        vault = self._create_test_vault(tmp_path)
        graph = LinkGraph()
        graph.scan_directory(vault)

        neighbors = graph.get_neighbors("note_a", hops=2)
        assert "note_b" in neighbors
        assert "note_c" in neighbors

    def test_orphan_no_links(self, tmp_path):
        vault = self._create_test_vault(tmp_path)
        graph = LinkGraph()
        graph.scan_directory(vault)

        orphan = graph.nodes["orphan"]
        assert len(orphan.out_links) == 0
        assert len(orphan.in_links) == 0

    def test_stats(self, tmp_path):
        vault = self._create_test_vault(tmp_path)
        graph = LinkGraph()
        graph.scan_directory(vault)

        stats = graph.get_stats()
        assert stats.total_nodes == 4
        assert stats.total_edges > 0

    def test_save_and_load(self, tmp_path):
        vault = self._create_test_vault(tmp_path)
        graph = LinkGraph()
        graph.scan_directory(vault)

        save_path = tmp_path / "graph.json"
        graph.save(save_path)
        assert save_path.exists()

        # Reload
        graph2 = LinkGraph()
        loaded = graph2.load(save_path)
        assert loaded is True
        assert len(graph2.nodes) == len(graph.nodes)
        assert "note_a" in graph2.nodes

    def test_load_nonexistent(self, tmp_path):
        graph = LinkGraph()
        loaded = graph.load(tmp_path / "nonexistent.json")
        assert loaded is False

    def test_to_mermaid(self, tmp_path):
        vault = self._create_test_vault(tmp_path)
        graph = LinkGraph()
        graph.scan_directory(vault)

        mermaid = graph.to_mermaid()
        assert "graph LR" in mermaid
        assert "note_a" in mermaid

    def test_extract_links_wikilink_with_alias(self):
        graph = LinkGraph()
        content = "See [[target_page|display text]] for details."
        links = graph._extract_links(content)
        assert "target_page" in links

    def test_extract_links_markdown(self):
        graph = LinkGraph()
        content = "See [my link](file:///path/to/file.md) here."
        links = graph._extract_links(content)
        assert "file" in links

    def test_nonexistent_directory(self):
        graph = LinkGraph()
        count = graph.scan_directory(Path("/nonexistent/path"))
        assert count == 0

    def test_detect_source_type(self):
        graph = LinkGraph()
        assert graph._detect_source_type(Path("handoff_2026.md")) == "handoff"
        assert graph._detect_source_type(Path("2026_conv_1_test.md")) == "session"
        assert graph._detect_source_type(Path("insight_001.md")) == "ki"
        assert graph._detect_source_type(Path("/kernel/axiom.md")) == "kernel"
