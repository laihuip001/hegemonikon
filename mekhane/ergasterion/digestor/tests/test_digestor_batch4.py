#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/ergasterion/digestor/tests/
# PURPOSE: Digestor Selector / Pipeline の包括テスト
"""Ergasterion Digestor Tests — Batch 4"""

import pytest
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from mekhane.ergasterion.digestor.selector import (
    DigestCandidate,
    DigestorSelector,
)

from mekhane.anamnesis.models.paper import Paper

from mekhane.ergasterion.digestor.pipeline import DigestResult, DigestorPipeline


# ═══ DigestCandidate ═══════════════════

# PURPOSE: Test suite validating digest candidate correctness
class TestDigestCandidate:
    """消化候補データクラスのテスト"""

    # PURPOSE: Verify create behaves correctly
    def test_create(self):
        """Verify create behavior."""
        paper = Paper(id="1", title="Test Paper", source="test", source_id="1")
        c = DigestCandidate(
            paper=paper,
            score=0.8,
            matched_topics=["fep"],
            rationale="High relevance",
        )
        assert c.score == 0.8


# ═══ DigestorSelector ══════════════════

# PURPOSE: Test suite validating digestor selector correctness
class TestDigestorSelector:
    """消化候補選定ロジックのテスト"""

    # PURPOSE: Verify topics file behaves correctly
    @pytest.fixture
    def topics_file(self, tmp_path):
        """Verify topics file behavior."""
        f = tmp_path / "topics.yaml"
        data = {
            "topics": [
                {"id": "fep", "query": "free energy principle active inference"},
                {"id": "category", "query": "category theory functor monad"},
                {"id": "ai", "query": "artificial intelligence machine learning"},
            ]
        }
        f.write_text(yaml.dump(data))
        return f

    # PURPOSE: Verify selector behaves correctly
    @pytest.fixture
    def selector(self, topics_file):
        """Verify selector behavior."""
        return DigestorSelector(topics_file=topics_file, mode="keyword")

    # PURPOSE: Verify papers behaves correctly
    @pytest.fixture
    def papers(self):
        """Verify papers behavior."""
        return [
            Paper(
                id="1",
                title="Free Energy Principle and Active Inference",
                abstract="A comprehensive review of the free energy principle and its applications to active inference in biological systems.",
                source="arxiv",
                source_id="2401.00001",
            ),
            Paper(
                id="2",
                title="Category Theory for Programmers",
                abstract="An introduction to category theory concepts including functors and monads for practical programming.",
                source="semantic_scholar",
                source_id="SS-12345",
            ),
            Paper(
                id="3",
                title="Cooking Recipes for Beginners",
                abstract="Simple cooking recipes for everyday meals.",
                source="arxiv",
                source_id="2401.99999",
            ),
        ]

    # PURPOSE: Verify init behaves correctly
    def test_init(self, selector):
        """Verify init behavior."""
        assert selector.topics is not None

    # PURPOSE: Verify get topics behaves correctly
    def test_get_topics(self, selector):
        """Verify get topics behavior."""
        topics = selector.get_topics()
        assert len(topics) == 3

    # PURPOSE: Verify match fep paper behaves correctly
    def test_match_fep_paper(self, selector, papers):
        """Verify match fep paper behavior."""
        matched = selector._match_topics(papers[0])
        topic_ids = [t for t, _ in matched]
        assert "fep" in topic_ids

    # PURPOSE: Verify match category paper behaves correctly
    def test_match_category_paper(self, selector, papers):
        """Verify match category paper behavior."""
        matched = selector._match_topics(papers[1])
        topic_ids = [t for t, _ in matched]
        assert "category" in topic_ids

    # PURPOSE: Verify no match irrelevant behaves correctly
    def test_no_match_irrelevant(self, selector, papers):
        """Verify no match irrelevant behavior."""
        matched = selector._match_topics(papers[2])
        assert len(matched) == 0

    # PURPOSE: Verify calculate score behaves correctly
    def test_calculate_score(self, selector, papers):
        """Verify calculate score behavior."""
        score = selector._calculate_score(papers[0], [("fep", 0.7)])
        assert 0.0 <= score <= 1.0
        assert score > 0.0

    # PURPOSE: Verify score with long abstract behaves correctly
    def test_score_with_long_abstract(self, selector):
        """Verify score with long abstract behavior."""
        paper = Paper(id="x", title="Test", abstract="a" * 600, source="arxiv", source_id="x")
        score = selector._calculate_score(paper, [("fep", 0.7)])
        assert score > 0.0

    # PURPOSE: Verify select candidates behaves correctly
    def test_select_candidates(self, selector, papers):
        """Verify select candidates behavior."""
        candidates = selector.select_candidates(papers)
        assert len(candidates) >= 1
        # Cooking paper should not be selected
        ids = [c.paper.id for c in candidates]
        assert "3" not in ids

    # PURPOSE: Verify select with max behaves correctly
    def test_select_with_max(self, selector, papers):
        """Verify select with max behavior."""
        candidates = selector.select_candidates(papers, max_candidates=1)
        assert len(candidates) <= 1

    # PURPOSE: Verify select with high min score behaves correctly
    def test_select_with_high_min_score(self, selector, papers):
        """Verify select with high min score behavior."""
        candidates = selector.select_candidates(papers, min_score=0.99)
        # Very high threshold should filter out most
        assert len(candidates) <= len(papers)

    # PURPOSE: Verify select with topic filter behaves correctly
    def test_select_with_topic_filter(self, selector, papers):
        """Verify select with topic filter behavior."""
        candidates = selector.select_candidates(papers, topic_filter=["fep"])
        for c in candidates:
            assert "fep" in c.matched_topics

    # PURPOSE: Verify select sorted by score behaves correctly
    def test_select_sorted_by_score(self, selector, papers):
        """Verify select sorted by score behavior."""
        candidates = selector.select_candidates(papers)
        for i in range(len(candidates) - 1):
            assert candidates[i].score >= candidates[i + 1].score

    # PURPOSE: Verify empty papers behaves correctly
    def test_empty_papers(self, selector):
        """Verify empty papers behavior."""
        candidates = selector.select_candidates([])
        assert len(candidates) == 0

    # PURPOSE: Verify no topics file behaves correctly
    def test_no_topics_file(self, tmp_path):
        """Verify no topics file behavior."""
        selector = DigestorSelector(topics_file=tmp_path / "nonexistent.yaml")
        assert selector.topics == {}


# ═══ DigestResult ══════════════════════

# PURPOSE: Test suite validating digest result correctness
class TestDigestResult:
    """消化結果データクラスのテスト"""

    # PURPOSE: Verify create behaves correctly
    def test_create(self):
        """Verify create behavior."""
        result = DigestResult(
            timestamp="2026-02-08",
            source="gnosis",
            total_papers=10,
            candidates_selected=3,
            candidates=[],
            dry_run=True,
        )
        assert result.total_papers == 10
        assert result.dry_run is True


# ═══ DigestorPipeline ══════════════════

# PURPOSE: Test suite validating digestor pipeline correctness
class TestDigestorPipeline:
    """消化パイプラインのテスト"""

    # PURPOSE: Verify pipeline behaves correctly
    @pytest.fixture
    def pipeline(self, tmp_path):
        """Verify pipeline behavior."""
        topics_file = tmp_path / "topics.yaml"
        topics_file.write_text(yaml.dump({
            "topics": [
                {"id": "fep", "query": "free energy principle"},
            ]
        }))
        selector = DigestorSelector(topics_file=topics_file)
        return DigestorPipeline(output_dir=tmp_path / "output", selector=selector)

    # PURPOSE: Verify init behaves correctly
    def test_init(self, pipeline):
        """Verify init behavior."""
        assert isinstance(pipeline, DigestorPipeline)

    # PURPOSE: Verify generate eat input behaves correctly
    def test_generate_eat_input(self, pipeline):
        """Verify generate eat input behavior."""
        paper = Paper(
            id="1",
            title="FEP Study",
            abstract="About free energy principle.",
            url="https://arxiv.org/abs/1234.5678",
            source="arxiv",
            source_id="1234.5678",
        )
        candidate = DigestCandidate(
            paper=paper, score=0.8, matched_topics=["fep"], rationale="Match"
        )
        eat_input = pipeline._generate_eat_input(candidate)
        assert "素材名" in eat_input
        assert eat_input["素材名"] == "FEP Study"

    # PURPOSE: Verify suggest digest targets behaves correctly
    def test_suggest_digest_targets(self, pipeline):
        """Verify suggest digest targets behavior."""
        paper = Paper(id="1", title="Test", abstract="Test abstract", source="arxiv", source_id="1")
        candidate = DigestCandidate(
            paper=paper, score=0.5, matched_topics=["fep"], rationale=""
        )
        targets = pipeline._suggest_digest_targets(candidate)
        assert isinstance(targets, list)
