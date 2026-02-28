# PROOF: [L2/テスト] <- mekhane/tests/
"""
PROOF: [L2/テスト] このファイルは存在しなければならない

A0 → kalon_checker.py の品質検証が正しく動作することを保証する必要がある
   → テストなき品質検証は自己矛盾
   → test_kalon_checker.py が担う

Q.E.D.
"""
import sys
from pathlib import Path

# Add project root to sys.path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from mekhane.fep.category import (
    ADJOINT_PAIRS_D,
    SERIES_ENRICHMENTS,
    AdjointPair,
    Enrichment,
    EnrichmentType,
    GaloisConnection,
    Series,
)
from mekhane.fep.kalon_checker import (
    KalonChecker,
    KalonLevel,
    KalonReport,
    KalonResult,
)


# =============================================================================
# KalonResult tests
# =============================================================================
class TestKalonResult:
    """Test KalonResult data class."""

    # PURPOSE: Test that KALON level means is_kalon is True
    def test_is_kalon_true(self):
        result = KalonResult(name="test", level=KalonLevel.KALON, score=1.0)
        assert result.is_kalon is True

    # PURPOSE: Test that non-KALON levels mean is_kalon is False
    def test_is_kalon_false(self):
        for level in (KalonLevel.APPROACHING, KalonLevel.INCOMPLETE, KalonLevel.ABSENT):
            result = KalonResult(name="test", level=level, score=0.5)
            assert result.is_kalon is False


# =============================================================================
# KalonReport tests
# =============================================================================
class TestKalonReport:
    """Test KalonReport aggregation."""

    # PURPOSE: Empty report should be ABSENT
    def test_empty_report(self):
        report = KalonReport()
        assert report.overall_level == KalonLevel.ABSENT
        assert report.overall_score == 0.0

    # PURPOSE: All KALON results → overall KALON
    def test_all_kalon(self):
        report = KalonReport(results=[
            KalonResult(name="a", level=KalonLevel.KALON, score=1.0),
            KalonResult(name="b", level=KalonLevel.KALON, score=0.9),
        ])
        assert report.overall_level == KalonLevel.KALON
        assert report.overall_score == pytest.approx(0.95)

    # PURPOSE: Mix of KALON and APPROACHING → APPROACHING
    def test_mixed_kalon_approaching(self):
        report = KalonReport(results=[
            KalonResult(name="a", level=KalonLevel.KALON, score=1.0),
            KalonResult(name="b", level=KalonLevel.APPROACHING, score=0.8),
        ])
        assert report.overall_level == KalonLevel.APPROACHING

    # PURPOSE: Any ABSENT → INCOMPLETE
    def test_any_absent(self):
        report = KalonReport(results=[
            KalonResult(name="a", level=KalonLevel.KALON, score=1.0),
            KalonResult(name="b", level=KalonLevel.ABSENT, score=0.0),
        ])
        assert report.overall_level == KalonLevel.INCOMPLETE

    # PURPOSE: Issues are collected from all results
    def test_all_issues(self):
        report = KalonReport(results=[
            KalonResult(name="a", level=KalonLevel.KALON, score=1.0, issues=["x"]),
            KalonResult(name="b", level=KalonLevel.APPROACHING, score=0.8, issues=["y", "z"]),
        ])
        assert len(report.all_issues) == 3
        assert "[a] x" in report.all_issues

    # PURPOSE: Summary line is formatted correctly
    def test_summary(self):
        report = KalonReport(results=[
            KalonResult(name="a", level=KalonLevel.KALON, score=1.0),
        ])
        summary = report.summary()
        assert "1/1" in summary
        assert "kalon" in summary


# =============================================================================
# KalonChecker with real data (category.py)
# =============================================================================
class TestKalonCheckerRealData:
    """Test KalonChecker against actual SERIES_ENRICHMENTS and ADJOINT_PAIRS_D."""

    def setup_method(self):
        self.checker = KalonChecker()

    # PURPOSE: Enrichment completeness should pass (all 6 series defined)
    def test_enrichment_completeness(self):
        result = self.checker.check_enrichment_completeness()
        assert result.level == KalonLevel.KALON
        assert result.score == 1.0

    # PURPOSE: Enrichment quality should pass (all scores >= 0.70)
    def test_enrichment_quality(self):
        result = self.checker.check_enrichment_quality()
        assert result.level in (KalonLevel.KALON, KalonLevel.APPROACHING)
        assert result.score >= 0.70

    # PURPOSE: All 12 adjoint pairs should be present
    def test_adjoint_completeness(self):
        result = self.checker.check_adjoint_completeness()
        assert result.level == KalonLevel.KALON
        assert result.score == 1.0

    # PURPOSE: All adjoint pairs should have valid structure
    def test_adjoint_symmetry(self):
        result = self.checker.check_adjoint_symmetry()
        assert result.level == KalonLevel.KALON

    # PURPOSE: All adjoint pairs should derive valid Galois connections
    def test_galois_derivability(self):
        result = self.checker.check_galois_derivability()
        assert result.level == KalonLevel.KALON
        assert result.score == 1.0

    # PURPOSE: check_all should return a valid report
    def test_check_all(self):
        report = self.checker.check_all()
        assert len(report.results) == 5
        assert report.overall_score >= 0.70
        assert report.overall_level in (KalonLevel.KALON, KalonLevel.APPROACHING)


# =============================================================================
# KalonChecker with synthetic data (edge cases)
# =============================================================================
class TestKalonCheckerEdgeCases:
    """Test KalonChecker with synthetic data for edge cases."""

    # PURPOSE: Missing enrichment should be detected
    def test_missing_enrichment(self):
        partial = {k: v for k, v in SERIES_ENRICHMENTS.items() if k != Series.O}
        checker = KalonChecker(enrichments=partial)
        result = checker.check_enrichment_completeness()
        assert result.level == KalonLevel.INCOMPLETE
        assert "Ousia" in result.issues[0]

    # PURPOSE: Low kalon score should fail quality check
    def test_low_kalon_score(self):
        low_quality = dict(SERIES_ENRICHMENTS)
        low_quality[Series.O] = Enrichment(
            type=EnrichmentType.END,
            concept="test",
            kalon=0.30,
            structures=("a",),
        )
        checker = KalonChecker(enrichments=low_quality)
        result = checker.check_enrichment_quality()
        assert len(result.issues) > 0

    # PURPOSE: Missing adjoint pair should be detected
    def test_missing_adjoint(self):
        partial = {k: v for k, v in ADJOINT_PAIRS_D.items() if k != "O-D1"}
        checker = KalonChecker(adjoint_pairs=partial)
        result = checker.check_adjoint_completeness()
        assert result.level == KalonLevel.INCOMPLETE
        assert "O-D1" in result.issues[0]

    # PURPOSE: Custom threshold should be respected
    def test_custom_threshold(self):
        # Set threshold very high (0.95) — most enrichments won't pass
        checker = KalonChecker(kalon_threshold=0.95)
        result = checker.check_enrichment_quality()
        # At least some should fail with threshold=0.95
        assert result.score < 0.95 or result.level != KalonLevel.KALON
