#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/ergasterion/digestor/tests/
# PURPOSE: Exa 統合テスト — _fetch_from_exa, _exa_to_paper
"""Exa Integration Tests — Phase C of DigestorPipeline"""

import pytest
from dataclasses import dataclass, field
from typing import Optional
from unittest.mock import patch, MagicMock, AsyncMock


# ═══ テスト用モック ═══════════════════════════════

# PURPOSE: テスト用の Paper モック
@dataclass
class MockPaper:
    """テスト用の Paper モック"""
    id: str
    title: str
    abstract: str = ""
    source: str = "exa"
    source_id: str = ""
    categories: list = field(default_factory=list)
    published: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None

    # PURPOSE: primary_key の処理
    @property
    def primary_key(self):
        return f"{self.source}:{self.source_id or self.id}"


# PURPOSE: Exa SearchResult のモック
@dataclass
class MockSearchResult:
    """Exa SearchResult のモック"""
    title: str = "Test Paper"
    url: str = "https://example.com/paper"
    content: str = "This is the paper content about active inference."
    snippet: str = "Active inference paper."
    relevance: float = 0.9
    timestamp: str = "2026-01-15"


# ═══ Phase C: Exa 統合 ═══════════════════════════


# PURPOSE: _exa_to_paper の単体テスト
class TestExaToPaper:
    """_exa_to_paper の単体テスト"""

    # PURPOSE: pipeline の処理
    @pytest.fixture
    def pipeline(self, tmp_path):
        topics_file = tmp_path / "topics.yaml"
        topics_file.write_text("""
settings:
  max_candidates: 10
  min_score: 0.45
  match_mode: keyword
topics:
  - id: fep
    query: "Free Energy Principle"
    digest_to: ["/noe"]
    description: FEP
""")
        from mekhane.ergasterion.digestor.pipeline import DigestorPipeline
        from mekhane.ergasterion.digestor.selector import DigestorSelector
        selector = DigestorSelector(topics_file=topics_file)
        return DigestorPipeline(output_dir=tmp_path, selector=selector)

    # PURPOSE: SearchResult → Paper 変換が成功する
    def test_converts_search_result(self, pipeline):
        """SearchResult → Paper 変換が成功する"""
        result = MockSearchResult(
            title="Active Inference and FEP",
            url="https://arxiv.org/abs/2601.12345",
            content="A paper about active inference frameworks.",
        )
        paper = pipeline._exa_to_paper(result, "fep")
        assert paper is not None
        assert paper.title == "Active Inference and FEP"
        assert paper.source == "exa"
        assert paper.url == "https://arxiv.org/abs/2601.12345"
        assert "active inference" in paper.abstract.lower()

    # PURPOSE: タイトルなし → None
    def test_empty_title_returns_none(self, pipeline):
        """タイトルなし → None"""
        result = MockSearchResult(title="", url="https://example.com")
        paper = pipeline._exa_to_paper(result, "fep")
        assert paper is None

    # PURPOSE: 空白のみタイトル → None
    def test_whitespace_title_returns_none(self, pipeline):
        """空白のみタイトル → None"""
        result = MockSearchResult(title="   ", url="https://example.com")
        paper = pipeline._exa_to_paper(result, "fep")
        assert paper is None

    # PURPOSE: content が 500 文字に切り詰められる
    def test_content_truncated_to_500(self, pipeline):
        """content が 500 文字に切り詰められる"""
        long_content = "x" * 1000
        result = MockSearchResult(title="Test", content=long_content)
        paper = pipeline._exa_to_paper(result, "fep")
        assert paper is not None
        assert len(paper.abstract) <= 500

    # PURPOSE: content が空の場合 snippet にフォールバック
    def test_fallback_to_snippet(self, pipeline):
        """content が空の場合 snippet にフォールバック"""
        result = MockSearchResult(title="Test", content="", snippet="Short snippet.")
        paper = pipeline._exa_to_paper(result, "fep")
        assert paper is not None
        assert paper.abstract == "Short snippet."


# PURPOSE: _fetch_from_exa の統合テスト
class TestFetchFromExa:
    """_fetch_from_exa の統合テスト"""

    # PURPOSE: pipeline の処理
    @pytest.fixture
    def pipeline(self, tmp_path):
        topics_file = tmp_path / "topics.yaml"
        topics_file.write_text("""
settings:
  max_candidates: 10
  min_score: 0.45
  match_mode: keyword
topics:
  - id: fep
    query: "Free Energy Principle"
    digest_to: ["/noe"]
    description: FEP
""")
        from mekhane.ergasterion.digestor.pipeline import DigestorPipeline
        from mekhane.ergasterion.digestor.selector import DigestorSelector
        selector = DigestorSelector(topics_file=topics_file)
        return DigestorPipeline(output_dir=tmp_path, selector=selector)

    # PURPOSE: EXA_API_KEY なし → 空リスト
    def test_skips_without_api_key(self, pipeline):
        """EXA_API_KEY なし → 空リスト"""
        with patch.dict("os.environ", {}, clear=True):
            # Ensure EXA_API_KEY is not set
            import os
            os.environ.pop("EXA_API_KEY", None)
            result = pipeline._fetch_from_exa(topics=["fep"])
            assert result == []

    # PURPOSE: EXA_API_KEY あり + mock → Paper リスト
    @patch("mekhane.periskope.searchers.exa_searcher.ExaSearcher")
    def test_returns_papers_with_api_key(self, mock_exa_cls, pipeline):
        """EXA_API_KEY あり + mock → Paper リスト"""
        mock_searcher = MagicMock()
        mock_exa_cls.return_value = mock_searcher

        mock_results = [
            MockSearchResult(title="Paper 1", content="Content 1"),
            MockSearchResult(title="Paper 2", content="Content 2"),
        ]
        mock_searcher.search_academic = AsyncMock(return_value=mock_results)

        with patch.dict("os.environ", {"EXA_API_KEY": "test-key"}):
            papers = pipeline._fetch_from_exa(topics=["fep"], max_papers=5)

        assert len(papers) == 2
        assert all(p.source == "exa" for p in papers)

    # PURPOSE: ExaSearcher が import できない → 空リスト
    def test_graceful_on_import_error(self, pipeline):
        """ExaSearcher が import できない → 空リスト"""
        with patch.dict("os.environ", {"EXA_API_KEY": "test-key"}):
            with patch.dict("sys.modules", {"mekhane.periskope.searchers.exa_searcher": None}):
                result = pipeline._fetch_from_exa(topics=["fep"])
                assert result == []
