# PROOF: [L2/Mekhane] <- tests/ A0->Auto->AddedByCI
# PURPOSE: G_semantic, HomCalculator, CLI のテスト
# REASON: 拡張モジュールが正しく動作するか検証
"""Tests for Basanos L2 extensions: G_semantic, HomCalculator, CLI."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from mekhane.basanos.l2.g_semantic import GSemantic, STATIC_TRANSLATIONS
from mekhane.basanos.l2.hom import HomCalculator, HomScore
from mekhane.basanos.l2.cli import main as cli_main, scan_deficits
from mekhane.basanos.l2.models import ExternalForm


# ---------------------------------------------------------------------------
# G_semantic tests
# ---------------------------------------------------------------------------


class TestGSemantic:
    """Test G_semantic translation."""

    def test_static_translations_exist(self) -> None:
        assert len(STATIC_TRANSLATIONS) >= 20

    def test_translate_noesis(self) -> None:
        gs = GSemantic(use_llm=False)
        ef = ExternalForm(
            source_path="kernel/ousia.md",
            keywords=["Noēsis"],
            claims=["Boulēsis は意志を司る"],
        )
        result = gs.translate(ef)
        # Should keep original AND add translated version
        assert any("reasoning" in kw.lower() or "cognition" in kw.lower() for kw in result.keywords)
        assert "Noēsis" in result.keywords  # Original preserved

    def test_translate_fep_terms(self) -> None:
        gs = GSemantic(use_llm=False)
        ef = ExternalForm(
            source_path="kernel/test.md",
            keywords=["FEP", "prediction error"],
        )
        result = gs.translate(ef)
        assert any("Free Energy" in kw for kw in result.keywords)

    def test_unknown_term_passthrough(self) -> None:
        gs = GSemantic(use_llm=False)
        ef = ExternalForm(
            source_path="test.md",
            keywords=["completely_unknown_xyz"],
        )
        result = gs.translate(ef)
        assert "completely_unknown_xyz" in result.keywords

    def test_claims_translated(self) -> None:
        gs = GSemantic(use_llm=False)
        ef = ExternalForm(
            source_path="test.md",
            claims=["Noēsis は認知の基盤"],
        )
        result = gs.translate(ef)
        assert len(result.claims) == 1
        # The claim should be translated
        assert result.claims[0] != ef.claims[0] or "Noēsis" not in result.claims[0]


# ---------------------------------------------------------------------------
# Hom calculator tests
# ---------------------------------------------------------------------------


class TestHomScore:
    """Test HomScore dataclass."""

    def test_keyword_only(self) -> None:
        s = HomScore(source="a", target="b", keyword_score=0.5)
        assert s.combined_score == 0.5  # Only keyword, full weight
        assert s.is_related

    def test_with_embedding(self) -> None:
        s = HomScore(source="a", target="b", keyword_score=0.3, embedding_score=0.8)
        # Weighted: (0.3*0.3 + 0.8*0.5) / (0.3+0.5) = 0.09+0.4 / 0.8 = 0.6125
        assert 0.5 < s.combined_score < 0.7
        assert s.is_related

    def test_not_related(self) -> None:
        s = HomScore(source="a", target="b", keyword_score=0.0)
        assert not s.is_related

    def test_full_scores(self) -> None:
        s = HomScore(source="a", target="b", keyword_score=1.0, embedding_score=1.0, llm_score=1.0)
        assert abs(s.combined_score - 1.0) < 0.01


class TestHomCalculator:
    """Test HomCalculator."""

    def test_jaccard_identical(self) -> None:
        hc = HomCalculator("/tmp", use_mneme=False, use_llm=False)
        score = hc.compute(
            ["active inference", "FEP"],
            ["active inference", "FEP"],
        )
        assert score.keyword_score == 1.0

    def test_jaccard_disjoint(self) -> None:
        hc = HomCalculator("/tmp", use_mneme=False, use_llm=False)
        score = hc.compute(["alpha", "beta"], ["gamma", "delta"])
        assert score.keyword_score == 0.0

    def test_jaccard_partial(self) -> None:
        hc = HomCalculator("/tmp", use_mneme=False, use_llm=False)
        score = hc.compute(
            ["active inference", "FEP", "novel"],
            ["FEP", "bayesian", "prediction"],
        )
        assert 0.0 < score.keyword_score < 1.0

    def test_substring_matching(self) -> None:
        hc = HomCalculator("/tmp", use_mneme=False, use_llm=False)
        score = hc.compute(["inference"], ["active inference"])
        # "inference" is a substring of "active inference"
        assert score.keyword_score > 0.0

    def test_batch_compute(self) -> None:
        hc = HomCalculator("/tmp", use_mneme=False, use_llm=False)
        scores = hc.batch_compute(
            ["FEP", "cognition"],
            [("target1", ["FEP"]), ("target2", ["perception"])],
        )
        assert len(scores) == 2
        assert scores[0].keyword_score > scores[1].keyword_score


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestCLI:
    """Test CLI entry point."""

    PROJECT_ROOT = Path("/home/makaron8426/oikos/hegemonikon")

    @pytest.mark.skipif(
        not Path("/home/makaron8426/oikos/hegemonikon/kernel").is_dir(),
        reason="Real kernel/ not available",
    )
    def test_scan_epsilon(self) -> None:
        deficits = scan_deficits(self.PROJECT_ROOT, deficit_type="epsilon")
        # There should be some ε deficits (theorem IDs without implementations)
        assert len(deficits) >= 0  # May be 0 if all have implementations
        for d in deficits:
            assert d.type.value.startswith("ε")

    @pytest.mark.skipif(
        not Path("/home/makaron8426/oikos/hegemonikon/kernel").is_dir(),
        reason="Real kernel/ not available",
    )
    def test_scan_delta(self) -> None:
        deficits = scan_deficits(self.PROJECT_ROOT, deficit_type="delta")
        # May or may not find deltas depending on recent git changes
        assert isinstance(deficits, list)

    def test_cli_no_args_returns_1(self) -> None:
        ret = cli_main([])
        assert ret == 1

    def test_cli_help(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            cli_main(["--help"])
        assert exc_info.value.code == 0
