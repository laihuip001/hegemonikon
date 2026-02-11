#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/anamnesis/tests/
# PURPOSE: Paper model の包括テスト
"""Anamnesis Paper Model Tests — Batch 5"""

import pytest
from mekhane.anamnesis.models.paper import Paper, merge_papers


# ═══ Paper Identity ════════════════════

# PURPOSE: Test suite validating paper identity correctness
class TestPaperIdentity:
    """Paper データクラス基本テスト"""

    # PURPOSE: Verify create minimal behaves correctly
    def test_create_minimal(self):
        """Verify create minimal behavior."""
        p = Paper(id="1", source="arxiv", source_id="2401.00001")
        assert p.id == "1"
        assert p.source == "arxiv"

    # PURPOSE: Verify create full behaves correctly
    def test_create_full(self):
        """Verify create full behavior."""
        p = Paper(
            id="1", source="arxiv", source_id="2401.00001",
            title="Test Paper", abstract="Abstract text",
            doi="10.1234/test", url="https://example.com",
        )
        assert p.title == "Test Paper"
        assert p.doi == "10.1234/test"

    # PURPOSE: Verify default fields behaves correctly
    def test_default_fields(self):
        """Verify default fields behavior."""
        p = Paper(id="1", source="arxiv", source_id="x")
        assert p.title == ""
        assert p.abstract == ""
        assert p.authors == []
        assert p.categories == []
        assert p.doi is None
        assert p.citations is None


# ═══ Primary Key ═══════════════════════

# PURPOSE: Test suite validating primary key correctness
class TestPrimaryKey:
    """重複排除用プライマリキーのテスト"""

    # PURPOSE: Verify primary key doi behaves correctly
    def test_primary_key_doi(self):
        """Verify primary key doi behavior."""
        p = Paper(id="1", source="arxiv", source_id="x", doi="10.1234/test")
        assert p.primary_key == "doi:10.1234/test"

    # PURPOSE: Verify primary key arxiv behaves correctly
    def test_primary_key_arxiv(self):
        """Verify primary key arxiv behavior."""
        p = Paper(id="1", source="arxiv", source_id="x", arxiv_id="2401.00001")
        assert p.primary_key == "arxiv:2401.00001"

    # PURPOSE: Verify primary key source behaves correctly
    def test_primary_key_source(self):
        """Verify primary key source behavior."""
        p = Paper(id="1", source="semantic_scholar", source_id="SS123")
        assert p.primary_key == "semantic_scholar:SS123"

    # PURPOSE: Verify primary key priority behaves correctly
    def test_primary_key_priority(self):
        # DOI should take priority over arXiv ID
        """Verify primary key priority behavior."""
        p = Paper(id="1", source="arxiv", source_id="x",
                  doi="10.1234/test", arxiv_id="2401.00001")
        assert p.primary_key == "doi:10.1234/test"


# ═══ Embedding Text ════════════════════

# PURPOSE: Test suite validating embedding text correctness
class TestEmbeddingText:
    """埋め込みテキスト生成テスト"""

    # PURPOSE: Verify embedding text behaves correctly
    def test_embedding_text(self):
        """Verify embedding text behavior."""
        p = Paper(id="1", source="arxiv", source_id="x",
                  title="My Paper", abstract="My abstract")
        assert "My Paper" in p.embedding_text
        assert "My abstract" in p.embedding_text

    # PURPOSE: Verify embedding truncation behaves correctly
    def test_embedding_truncation(self):
        """Verify embedding truncation behavior."""
        long_abstract = "a" * 2000
        p = Paper(id="1", source="arxiv", source_id="x",
                  title="Title", abstract=long_abstract)
        assert len(p.embedding_text) <= 1010  # title + space + 1000 chars


# ═══ Serialization ═════════════════════

# PURPOSE: Test suite validating serialization correctness
class TestSerialization:
    """to_dict / from_dict ラウンドトリップテスト"""

    # PURPOSE: Verify paper behaves correctly
    @pytest.fixture
    def paper(self):
        """Verify paper behavior."""
        return Paper(
            id="gnosis_arxiv_2401.00001",
            source="arxiv",
            source_id="2401.00001",
            doi="10.1234/test",
            arxiv_id="2401.00001",
            title="FEP Paper",
            authors=["Author A", "Author B"],
            abstract="Test abstract",
            published="2024-01-15",
            url="https://arxiv.org/abs/2401.00001",
            citations=42,
            categories=["cs.AI", "q-bio.NC"],
            venue="NeurIPS",
        )

    # PURPOSE: Verify to dict behaves correctly
    def test_to_dict(self, paper):
        """Verify to dict behavior."""
        d = paper.to_dict()
        assert d["id"] == "gnosis_arxiv_2401.00001"
        assert d["source"] == "arxiv"
        assert d["title"] == "FEP Paper"
        assert d["citations"] == 42

    # PURPOSE: Verify to dict authors join behaves correctly
    def test_to_dict_authors_join(self, paper):
        """Verify to dict authors join behavior."""
        d = paper.to_dict()
        assert "Author A" in d["authors"]
        assert "Author B" in d["authors"]

    # PURPOSE: Verify to dict categories join behaves correctly
    def test_to_dict_categories_join(self, paper):
        """Verify to dict categories join behavior."""
        d = paper.to_dict()
        assert "cs.AI" in d["categories"]

    # PURPOSE: Verify from dict behaves correctly
    def test_from_dict(self, paper):
        """Verify from dict behavior."""
        d = paper.to_dict()
        p2 = Paper.from_dict(d)
        assert p2.id == paper.id
        assert p2.source == paper.source
        assert p2.title == paper.title

    # PURPOSE: Verify roundtrip behaves correctly
    def test_roundtrip(self, paper):
        """Verify roundtrip behavior."""
        d = paper.to_dict()
        p2 = Paper.from_dict(d)
        assert p2.primary_key == paper.primary_key


# ═══ Merge ═════════════════════════════

# PURPOSE: Test suite validating merge papers correctness
class TestMergePapers:
    """論文マージのテスト"""

    # PURPOSE: Verify merge fills gaps behaves correctly
    def test_merge_fills_gaps(self):
        """Verify merge fills gaps behavior."""
        existing = Paper(id="1", source="arxiv", source_id="x",
                         title="Title", doi="10.1234/test")
        new = Paper(id="2", source="arxiv", source_id="x",
                    abstract="New abstract", citations=10)
        merged = merge_papers(existing, new)
        assert merged.title == "Title"  # existing kept
        assert merged.abstract == "New abstract"  # new fills gap
        assert merged.doi == "10.1234/test"  # existing kept

    # PURPOSE: Verify merge citations updated behaves correctly
    def test_merge_citations_updated(self):
        """Verify merge citations updated behavior."""
        existing = Paper(id="1", source="arxiv", source_id="x", citations=5)
        new = Paper(id="2", source="arxiv", source_id="x", citations=10)
        merged = merge_papers(existing, new)
        assert merged.citations == 10  # new wins

    # PURPOSE: Verify merge keeps existing id behaves correctly
    def test_merge_keeps_existing_id(self):
        """Verify merge keeps existing id behavior."""
        existing = Paper(id="existing_id", source="arxiv", source_id="x")
        new = Paper(id="new_id", source="arxiv", source_id="x")
        merged = merge_papers(existing, new)
        assert merged.id == "existing_id"

    # PURPOSE: Verify merge combines categories behaves correctly
    def test_merge_combines_categories(self):
        """Verify merge combines categories behavior."""
        existing = Paper(id="1", source="arxiv", source_id="x",
                         categories=["cs.AI"])
        new = Paper(id="2", source="arxiv", source_id="x",
                    categories=["q-bio.NC"])
        merged = merge_papers(existing, new)
        assert "cs.AI" in merged.categories
        assert "q-bio.NC" in merged.categories
