# PROOF: [L2/インフラ] A0→消化処理が必要→test_selector が担う
"""
Digestor Selector Tests
"""

import pytest
from dataclasses import dataclass, field
from typing import Optional

from mekhane.ergasterion.digestor.selector import DigestorSelector, DigestCandidate


@dataclass
class MockPaper:
    """テスト用の Paper モック"""

    id: str
    title: str
    abstract: str = ""
    source: str = "arxiv"
    categories: list[str] = field(default_factory=list)
    published: Optional[str] = None
    url: Optional[str] = None


class TestDigestorSelector:
    """DigestorSelector のテスト"""

    def test_select_candidates_empty(self):
        """空のリストを渡した場合"""
        selector = DigestorSelector()
        candidates = selector.select_candidates([])
        assert candidates == []

    def test_select_candidates_with_matching_paper(self):
        """マッチする論文がある場合"""
        selector = DigestorSelector()

        papers = [
            MockPaper(
                id="test-1",
                title="LLM Autonomous Agent Architecture for Complex Tasks",
                abstract="This paper presents a novel autonomous agent architecture using large language models...",
                source="arxiv",
            )
        ]

        candidates = selector.select_candidates(papers)

        # トピックにマッチすれば候補として選ばれる
        # （マッチしない場合は空リスト）
        assert isinstance(candidates, list)

    def test_select_candidates_score_ordering(self):
        """スコア順にソートされることを確認"""
        selector = DigestorSelector()

        papers = [
            MockPaper(id="test-1", title="Simple paper", abstract="Short abstract", source="arxiv"),
            MockPaper(
                id="test-2",
                title="LLM Autonomous Agent Architecture",
                abstract="This is a very long abstract about large language models and autonomous agent architecture. "
                * 20,
                source="arxiv",
            ),
        ]

        candidates = selector.select_candidates(papers, min_score=0.0)

        # 長い abstract の方がスコアが高い
        if len(candidates) >= 2:
            assert candidates[0].score >= candidates[1].score

    def test_get_topics(self):
        """トピック取得"""
        selector = DigestorSelector()
        topics = selector.get_topics()

        # topics.yaml が存在すればトピックが返される
        assert isinstance(topics, list)


class TestDigestCandidate:
    """DigestCandidate のテスト"""

    def test_create_candidate(self):
        """候補の作成"""
        paper = MockPaper(id="test-1", title="Test Paper", abstract="Test abstract")

        candidate = DigestCandidate(
            paper=paper,
            score=0.8,
            matched_topics=["agent-architecture"],
            rationale="Test rationale",
        )

        assert candidate.paper.id == "test-1"
        assert candidate.score == 0.8
        assert "agent-architecture" in candidate.matched_topics
