#!/usr/bin/env python3
"""Tests for drift_calculator.py — [0,1]-Enriched Category Hom Value

Tests the TF-IDF and coverage drift computation methods.
"""

import pytest

from mekhane.fep.drift_calculator import (
    DriftResult,
    compute_drift,
    describe_drift,
    _char_ngrams,
    _cosine_similarity,
    _normalize_text,
    _split_into_chunks,
)


# PURPOSE: Test suite validating char ngrams correctness
class TestCharNgrams:
    """Test character n-gram extraction."""

    # PURPOSE: Verify basic english behaves correctly
    def test_basic_english(self):
        """Verify basic english behavior."""
        ngrams = _char_ngrams("hello", n=2)
        assert ngrams == ["he", "el", "ll", "lo"]

    # PURPOSE: Verify basic japanese behaves correctly
    def test_basic_japanese(self):
        """Verify basic japanese behavior."""
        ngrams = _char_ngrams("圏論", n=2)
        assert ngrams == ["圏論"]

    # PURPOSE: Verify mixed text behaves correctly
    def test_mixed_text(self):
        """Verify mixed text behavior."""
        ngrams = _char_ngrams("HGK圏論", n=2)
        assert len(ngrams) == 4  # "hg", "gk", "k圏", "圏論"

    # PURPOSE: Verify short text behaves correctly
    def test_short_text(self):
        """Verify short text behavior."""
        ngrams = _char_ngrams("ab", n=3)
        assert ngrams == ["ab"]  # text shorter than n

    # PURPOSE: Verify empty text behaves correctly
    def test_empty_text(self):
        """Verify empty text behavior."""
        ngrams = _char_ngrams("", n=2)
        assert ngrams == []


# PURPOSE: Test suite validating normalize text correctness
class TestNormalizeText:
    """Test text normalization."""

    # PURPOSE: Verify markdown headers behaves correctly
    def test_markdown_headers(self):
        """Verify markdown headers behavior."""
        result = _normalize_text("## Hello World")
        assert "##" not in result
        assert "hello world" in result

    # PURPOSE: Verify code blocks behaves correctly
    def test_code_blocks(self):
        """Verify code blocks behavior."""
        result = _normalize_text("text ```code block``` more text")
        assert "code block" not in result

    # PURPOSE: Verify inline code behaves correctly
    def test_inline_code(self):
        """Verify inline code behavior."""
        result = _normalize_text("use `compute_drift()` function")
        assert "compute_drift()" not in result

    # PURPOSE: Verify yaml frontmatter behaves correctly
    def test_yaml_frontmatter(self):
        """Verify yaml frontmatter behavior."""
        result = _normalize_text("---\ntitle: test\n---\ncontent")
        assert "title" not in result
        assert "content" in result


# PURPOSE: Test suite validating split into chunks correctness
class TestSplitIntoChunks:
    """Test text chunking."""

    # PURPOSE: Verify paragraph split behaves correctly
    def test_paragraph_split(self):
        """Verify paragraph split behavior."""
        text = "First paragraph with enough content to pass minimum length.\n\nSecond paragraph with enough content to pass minimum length too."
        chunks = _split_into_chunks(text, min_length=20)
        assert len(chunks) == 2

    # PURPOSE: Verify merges short chunks behaves correctly
    def test_merges_short_chunks(self):
        """Verify merges short chunks behavior."""
        text = "Short\n\nAnother short\n\nThis is a longer paragraph with sufficient content."
        chunks = _split_into_chunks(text, min_length=30)
        # Short chunks should be merged
        assert len(chunks) <= 2

    # PURPOSE: Verify empty text behaves correctly
    def test_empty_text(self):
        """Verify empty text behavior."""
        chunks = _split_into_chunks("")
        assert chunks == []


# PURPOSE: Test suite validating cosine similarity correctness
class TestCosineSimilarity:
    """Test cosine similarity computation."""

    # PURPOSE: Verify identical vectors behaves correctly
    def test_identical_vectors(self):
        """Verify identical vectors behavior."""
        vec = [1.0, 2.0, 3.0]
        assert abs(_cosine_similarity(vec, vec) - 1.0) < 0.001

    # PURPOSE: Verify orthogonal vectors behaves correctly
    def test_orthogonal_vectors(self):
        """Verify orthogonal vectors behavior."""
        assert abs(_cosine_similarity([1, 0], [0, 1])) < 0.001

    # PURPOSE: Verify zero vector behaves correctly
    def test_zero_vector(self):
        """Verify zero vector behavior."""
        assert _cosine_similarity([0, 0], [1, 1]) == 0.0


# PURPOSE: Test suite validating compute drift correctness
class TestComputeDrift:
    """Test drift computation."""

    # PURPOSE: Verify identical texts behaves correctly
    def test_identical_texts(self):
        """Verify identical texts behavior."""
        text = "This is a test document with enough content. " * 5
        result = compute_drift(text, text, method="tfidf")
        assert result.value < 0.1  # Nearly identical
        assert result.method == "tfidf"

    # PURPOSE: Verify completely different texts behaves correctly
    def test_completely_different_texts(self):
        """Verify completely different texts behavior."""
        source = "圏論における前順序圏のガロア接続について議論した。随伴関手の定義と性質を確認した。" * 3
        compressed = "Python のデータクラスを使ったウェブアプリケーションの設計パターンについて。" * 3
        result = compute_drift(source, compressed, method="tfidf")
        assert result.value > 0.5  # High drift
        assert len(result.lost_chunks) > 0

    # PURPOSE: Verify partial overlap behaves correctly
    def test_partial_overlap(self):
        """Verify partial overlap behavior."""
        source = ("圏論の基本概念を説明した。関手と自然変換の定義を確認した。"
                  "\n\n"
                  "随伴関手の左と右の関係について議論した。ガロア接続との対応。"
                  "\n\n"
                  "雑談: 今日の天気は良かった。コーヒーを飲んだ。")
        compressed = ("圏論の基本概念: 関手と自然変換の定義。"
                      "\n\n"
                      "随伴関手: 左⊣右、ガロア接続との対応を確認。")
        result = compute_drift(source, compressed, method="tfidf")
        # Should be moderate drift (雑談 is lost)
        assert 0.1 < result.value < 0.8

    # PURPOSE: Verify empty source behaves correctly
    def test_empty_source(self):
        """Verify empty source behavior."""
        result = compute_drift("", "some compressed text")
        assert result.value == 0.0

    # PURPOSE: Verify empty compressed behaves correctly
    def test_empty_compressed(self):
        """Verify empty compressed behavior."""
        source = "Important information that should be preserved. " * 5
        result = compute_drift(source, "")
        assert result.value == 1.0

    # PURPOSE: Verify drift result properties behaves correctly
    def test_drift_result_properties(self):
        """Verify drift result properties behavior."""
        result = DriftResult(value=0.35, method="tfidf")
        assert result.preservation_rate == pytest.approx(0.65)
        assert result.lost_count == 0
        assert result.preserved_count == 0


# PURPOSE: Test suite validating coverage drift correctness
class TestCoverageDrift:
    """Test coverage-based drift computation."""

    # PURPOSE: Verify full coverage behaves correctly
    def test_full_coverage(self):
        """Verify full coverage behavior."""
        source = "## 圏論\n\n**随伴関手**の定義。\n\n## ガロア接続\n\n**前順序圏**の特殊ケース。"
        compressed = "圏論と随伴関手の定義。ガロア接続は前順序圏の特殊ケース。"
        result = compute_drift(source, compressed, method="coverage")
        assert result.value < 0.5  # Good coverage

    # PURPOSE: Verify no coverage behaves correctly
    def test_no_coverage(self):
        """Verify no coverage behavior."""
        source = "## 機械学習\n\n**ニューラルネットワーク**の訓練。"
        compressed = "今日の天気は晴れでした。"
        result = compute_drift(source, compressed, method="coverage")
        assert result.value > 0.5  # Poor coverage


# PURPOSE: Test suite validating describe drift correctness
class TestDescribeDrift:
    """Test human-readable output."""

    # PURPOSE: Verify low drift behaves correctly
    def test_low_drift(self):
        """Verify low drift behavior."""
        result = DriftResult(
            value=0.15,
            method="tfidf",
            preserved_chunks=["chunk1", "chunk2"],
            lost_chunks=[],
        )
        desc = describe_drift(result)
        assert "🟢" in desc
        assert "15.0%" in desc

    # PURPOSE: Verify high drift behaves correctly
    def test_high_drift(self):
        """Verify high drift behavior."""
        result = DriftResult(
            value=0.65,
            method="tfidf",
            lost_chunks=["important info lost"],
            preserved_chunks=["some preserved"],
        )
        desc = describe_drift(result)
        assert "🔴" in desc
        assert "❌" in desc
        assert "important info lost" in desc


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
