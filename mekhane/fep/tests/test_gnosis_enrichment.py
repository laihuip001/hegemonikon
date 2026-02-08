# PROOF: [L3/テスト] <- mekhane/fep/tests/
# PURPOSE: Gnōsis enrichment が AttractorAdvisor に正しく統合されているかを検証する
"""
Tests for AttractorAdvisor Gnōsis integration.

Verifies:
- knowledge_context field exists on Recommendation
- _retrieve_gnosis returns empty list when index is missing
- format_for_llm includes [Knowledge: ...] when context is present
- Gnōsis failure never blocks recommendations (graceful degradation)
"""

import pytest
from unittest.mock import patch, MagicMock
from dataclasses import fields

from mekhane.fep.attractor_advisor import AttractorAdvisor, Recommendation
from mekhane.fep.attractor import OscillationType, OscillationDiagnosis


def _make_interpretation() -> OscillationDiagnosis:
    """Test helper: create a minimal OscillationDiagnosis."""
    return OscillationDiagnosis(
        oscillation=OscillationType.CLEAR,
        theory="テスト理論",
        action="テスト行動",
        morphisms=[],
        confidence_modifier=0.0,
    )


# PURPOSE: Gnōsis × Attractor integration tests
class TestGnosisEnrichment:
    """Gnōsis × Attractor integration tests."""

    # PURPOSE: Recommendation dataclass has knowledge_context field
    def test_recommendation_has_knowledge_context_field(self):
        """Recommendation dataclass has knowledge_context field."""
        field_names = [f.name for f in fields(Recommendation)]
        assert "knowledge_context" in field_names

    # PURPOSE: Default knowledge_context is empty list
    def test_recommendation_knowledge_context_default_empty(self):
        """Default knowledge_context is empty list."""
        rec = Recommendation(
            advice="test",
            workflows=[],
            series=[],
            oscillation=OscillationType.CLEAR,
            confidence=0.0,
            interpretation=_make_interpretation(),
        )
        assert rec.knowledge_context == []

    # PURPOSE: AttractorAdvisor accepts use_gnosis parameter
    def test_advisor_has_use_gnosis_flag(self):
        """AttractorAdvisor accepts use_gnosis parameter."""
        advisor = AttractorAdvisor(force_cpu=True, use_gnosis=False)
        assert advisor._use_gnosis is False

    # PURPOSE: Gnōsis is enabled by default
    def test_advisor_default_gnosis_enabled(self):
        """Gnōsis is enabled by default."""
        advisor = AttractorAdvisor(force_cpu=True)
        assert advisor._use_gnosis is True

    # PURPOSE: _retrieve_gnosis always returns a list (empty or populated)
    def test_retrieve_gnosis_returns_list(self):
        """_retrieve_gnosis always returns a list (empty or populated)."""
        advisor = AttractorAdvisor(force_cpu=True)
        result = advisor._retrieve_gnosis("test query")
        assert isinstance(result, list)
        # Each item (if any) should be a dict with ki_name
        for item in result:
            assert "ki_name" in item

    # PURPOSE: _retrieve_gnosis returns empty on import error
    def test_retrieve_gnosis_graceful_on_import_error(self):
        """_retrieve_gnosis returns empty on import error."""
        advisor = AttractorAdvisor(force_cpu=True)
        # Simulate sophia_ingest being unavailable
        with patch.dict("sys.modules", {"mekhane.symploke.sophia_ingest": None}):
            result = advisor._retrieve_gnosis("test query")
            assert isinstance(result, list)

    # PURPOSE: format_for_llm outputs [Knowledge: ...] when knowledge_context is set
    def test_format_for_llm_includes_knowledge_line(self):
        """format_for_llm outputs [Knowledge: ...] when knowledge_context is set."""
        advisor = AttractorAdvisor(force_cpu=True, use_gnosis=False)

        mock_rec = Recommendation(
            advice="O-series に収束",
            workflows=["/noe"],
            series=["O"],
            oscillation=OscillationType.CLEAR,
            confidence=0.9,
            interpretation=_make_interpretation(),
            knowledge_context=[
                {"ki_name": "Core System", "summary": "test", "score": 0.85},
                {"ki_name": "FEP Theory", "summary": "test2", "score": 0.72},
            ],
        )

        with patch.object(advisor, "recommend", return_value=mock_rec):
            output = advisor.format_for_llm("なぜ")

        assert "[Knowledge:" in output
        assert "Core System" in output
        assert "FEP Theory" in output

    # PURPOSE: format_for_llm omits [Knowledge:] when no knowledge_context
    def test_format_for_llm_no_knowledge_when_empty(self):
        """format_for_llm omits [Knowledge:] when no knowledge_context."""
        advisor = AttractorAdvisor(force_cpu=True, use_gnosis=False)

        mock_rec = Recommendation(
            advice="O-series に収束",
            workflows=["/noe"],
            series=["O"],
            oscillation=OscillationType.CLEAR,
            confidence=0.9,
            interpretation=_make_interpretation(),
            knowledge_context=[],
        )

        with patch.object(advisor, "recommend", return_value=mock_rec):
            output = advisor.format_for_llm("なぜ")

        assert "[Knowledge:" not in output

    # PURPOSE: recommend() works without Gnōsis when use_gnosis=False
    def test_recommend_with_gnosis_disabled_no_crash(self):
        """recommend() works without Gnōsis when use_gnosis=False."""
        advisor = AttractorAdvisor(force_cpu=True, use_gnosis=False)

        # Mock the attractor to avoid needing ONNX model
        mock_result = MagicMock()
        mock_result.attractors = []
        mock_result.oscillation = OscillationType.WEAK
        mock_result.primary = None
        mock_result.interpretation = _make_interpretation()

        with patch.object(advisor._attractor, "diagnose", return_value=mock_result):
            rec = advisor.recommend("test")

        assert rec.knowledge_context == []

    # PURPOSE: recommend() with Gnōsis enabled completes (even without index)
    def test_recommend_with_gnosis_enabled_no_crash(self):
        """recommend() with Gnōsis enabled completes (even without index)."""
        advisor = AttractorAdvisor(force_cpu=True, use_gnosis=True)

        # Mock the attractor to avoid needing ONNX model
        mock_attractor_result = MagicMock()
        mock_attractor_result.attractors = [
            MagicMock(series="O", name="Noēsis", workflows=["/noe"])
        ]
        mock_attractor_result.primary = mock_attractor_result.attractors[0]
        mock_attractor_result.oscillation = OscillationType.CLEAR
        mock_attractor_result.top_similarity = 0.9
        mock_attractor_result.interpretation = _make_interpretation()

        with patch.object(advisor._attractor, "diagnose", return_value=mock_attractor_result):
            rec = advisor.recommend("なぜこのプロジェクトは存在するのか")

        assert rec.advice is not None
        assert isinstance(rec.knowledge_context, list)
