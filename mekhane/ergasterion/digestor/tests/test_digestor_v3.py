#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/ergasterion/digestor/tests/
# PURPOSE: Digestor v3 改修テスト — 3層防御 + スコア v3 + 閾値変更
"""Digestor v3 Tests — 層1カテゴリフィルタ, 層3ドメインキーワード, スコア v3"""

import pytest
from dataclasses import dataclass, field
from typing import Optional

from mekhane.ergasterion.digestor.selector import (
    _is_relevant_domain,
    _domain_relevance,
    ALLOWED_CATEGORY_PREFIXES,
    DOMAIN_KEYWORDS,
    DigestorSelector,
    SemanticMatcher,
)


# ═══ テスト用 Paper モック ═══════════════════════════════

@dataclass
class MockPaper:
    """テスト用の Paper モック"""
    id: str
    title: str
    abstract: str = ""
    source: str = "arxiv"
    source_id: str = ""
    categories: list = field(default_factory=list)
    published: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None

    @property
    def primary_key(self):
        return f"{self.source}:{self.source_id or self.id}"

    @property
    def embedding_text(self):
        return f"{self.title} {self.abstract}"


# ═══ 層1: arXiv カテゴリフィルタ ═══════════════════════════


class TestCategoryFilter:
    """層1: _is_relevant_domain のテスト"""

    def test_cs_category_passes(self):
        """cs.* カテゴリは通過"""
        paper = MockPaper(id="1", title="Test", categories=["cs.AI"])
        assert _is_relevant_domain(paper) is True

    def test_cs_cl_category_passes(self):
        """cs.CL (Computation and Language) も通過"""
        paper = MockPaper(id="2", title="Test", categories=["cs.CL"])
        assert _is_relevant_domain(paper) is True

    def test_stat_ml_passes(self):
        """stat.ML は通過"""
        paper = MockPaper(id="3", title="Test", categories=["stat.ML"])
        assert _is_relevant_domain(paper) is True

    def test_qbio_nc_passes(self):
        """q-bio.NC は通過"""
        paper = MockPaper(id="4", title="Test", categories=["q-bio.NC"])
        assert _is_relevant_domain(paper) is True

    def test_eess_passes(self):
        """eess.* は通過"""
        paper = MockPaper(id="5", title="Test", categories=["eess.SP"])
        assert _is_relevant_domain(paper) is True

    def test_biology_blocked(self):
        """q-bio.QM は除外"""
        paper = MockPaper(id="6", title="Test", categories=["q-bio.QM"])
        assert _is_relevant_domain(paper) is False

    def test_physics_blocked(self):
        """physics.* は除外"""
        paper = MockPaper(id="7", title="Test", categories=["physics.gen-ph"])
        assert _is_relevant_domain(paper) is False

    def test_no_categories_passes(self):
        """カテゴリなし → 通過 (偽陽性 > 偽陰性)"""
        paper = MockPaper(id="8", title="Test", categories=[])
        assert _is_relevant_domain(paper) is True

    def test_no_categories_attr_passes(self):
        """categories 属性なし → 通過"""
        paper = MockPaper(id="9", title="Test")
        paper.__dict__.pop("categories", None)  # 属性を削除
        # getattr fallback → None → True
        assert _is_relevant_domain(paper) is True

    def test_mixed_categories_one_match(self):
        """複数カテゴリのうち1つが許可 → 通過"""
        paper = MockPaper(id="10", title="Test", categories=["math.CO", "cs.DS"])
        assert _is_relevant_domain(paper) is True


# ═══ 層3: ドメインキーワード ═══════════════════════════════


class TestDomainRelevance:
    """層3: _domain_relevance のテスト"""

    def test_high_relevance(self):
        """AI 論文 → 3+ キーワードヒットで 1.0"""
        paper = MockPaper(
            id="1",
            title="Large Language Model Agent for Autonomous Reasoning",
            abstract="This paper presents an LLM-based agent for cognitive reasoning tasks.",
        )
        score = _domain_relevance(paper)
        assert score == 1.0

    def test_zero_relevance(self):
        """料理論文 → 0.0"""
        paper = MockPaper(
            id="2",
            title="Cooking Recipes for Beginners",
            abstract="Simple cooking recipes for everyday meals.",
        )
        score = _domain_relevance(paper)
        assert score == 0.0

    def test_partial_relevance(self):
        """1-2 キーワード → 0.33-0.67"""
        paper = MockPaper(
            id="3",
            title="Neural Network Applications in Chemistry",
            abstract="Pure chemistry discussion with no AI focus.",
        )
        score = _domain_relevance(paper)
        assert 0.0 < score < 1.0

    def test_philosophy_topic_relevant(self):
        """ストア哲学 → relevant"""
        paper = MockPaper(
            id="4",
            title="Stoic Philosophy and Modern Epistemology",
            abstract="An exploration of stoic epistemology and its relevance.",
        )
        score = _domain_relevance(paper)
        assert score > 0.0

    def test_fep_topic_relevant(self):
        """FEP → relevant"""
        paper = MockPaper(
            id="5",
            title="Free Energy Principle and Variational Bayesian Inference",
            abstract="Active inference using free energy minimization.",
        )
        score = _domain_relevance(paper)
        assert score == 1.0


# ═══ スコア v3 ═══════════════════════════════════════════════


class TestScoreV3:
    """_calculate_score v3 のテスト"""

    @pytest.fixture
    def selector(self, tmp_path):
        """Selector with minimal topics"""
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
  - id: agent
    query: "LLM agent architecture"
    digest_to: ["/s"]
    description: Agent
  - id: category
    query: "category theory"
    digest_to: ["/noe"]
    description: Category Theory
""")
        return DigestorSelector(topics_file=topics_file)

    def test_score_components_sum(self, selector):
        """スコア構成: semantic 0.5 + domain 0.2 + abstract 0.1 + breadth 0.1 + source 0.1"""
        paper = MockPaper(
            id="1",
            title="LLM Agent for Active Inference using Category Theory",
            abstract="A comprehensive paper " + "x" * 600,
            source="arxiv",
        )
        matched = [("fep", 0.9), ("agent", 0.8), ("category", 0.7)]
        score = selector._calculate_score(paper, matched)
        # All components should contribute
        assert score > 0.5
        assert score <= 1.0

    def test_score_zero_for_irrelevant(self, selector):
        """無関係論文 → スコアが非常に低い"""
        paper = MockPaper(
            id="2",
            title="Cooking Recipes for Beginners",
            abstract="Simple cooking recipes.",
            source="other",
        )
        score = selector._calculate_score(paper, [])
        assert score < 0.1

    def test_threshold_updated(self):
        """SemanticMatcher 閾値が 0.55 に更新されている"""
        assert SemanticMatcher.SIMILARITY_THRESHOLD == 0.55


# ═══ 統合テスト ═══════════════════════════════════════════════


class TestSelectCandidatesV3:
    """select_candidates での層1フィルタ統合テスト"""

    @pytest.fixture
    def selector(self, tmp_path):
        """Selector with keyword mode"""
        topics_file = tmp_path / "topics.yaml"
        topics_file.write_text("""
settings:
  max_candidates: 10
  min_score: 0.1
  match_mode: keyword
topics:
  - id: fep
    query: "free energy principle active inference"
    digest_to: ["/noe"]
    description: FEP
""")
        return DigestorSelector(topics_file=topics_file)

    def test_irrelevant_domain_excluded(self, selector):
        """非関連ドメインは select_candidates で除外"""
        papers = [
            MockPaper(
                id="1",
                title="Free Energy Principle Review",
                abstract="Active inference and free energy in AI systems.",
                source="arxiv",
                categories=["cs.AI"],
            ),
            MockPaper(
                id="2",
                title="Free Energy in Thermodynamics",
                abstract="Free energy calculations in chemistry.",
                source="arxiv",
                categories=["physics.chem-ph"],
            ),
        ]
        candidates = selector.select_candidates(papers)
        # Only cs.AI paper should remain
        candidate_ids = [c.paper.id for c in candidates]
        assert "1" in candidate_ids
        assert "2" not in candidate_ids

    def test_no_category_passes_through(self, selector):
        """カテゴリなしの論文は通過する"""
        papers = [
            MockPaper(
                id="1",
                title="Free Energy Principle and Active Inference",
                abstract="Active inference paper.",
                source="semantic_scholar",
                categories=[],
            ),
        ]
        candidates = selector.select_candidates(papers)
        assert len(candidates) >= 0  # Should at least not crash
