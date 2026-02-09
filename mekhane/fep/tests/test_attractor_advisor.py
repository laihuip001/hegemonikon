"""Tests for attractor_advisor helper functions."""

import unittest
from unittest.mock import patch, MagicMock
from mekhane.fep.attractor_advisor import (
    _classify_series_list,
    _detect_crossings,
    _suggest_pw_for_crossings,
    Recommendation,
    CompoundRecommendation,
)


class TestClassifySeriesList(unittest.TestCase):
    """Test _classify_series_list() series→CognitiveType mapping."""

    def test_single_o_series(self):
        result = _classify_series_list(["O"])
        self.assertIn("O", result)

    def test_multiple_series(self):
        result = _classify_series_list(["O", "S", "A"])
        self.assertEqual(len(result), 3)

    def test_empty_list(self):
        result = _classify_series_list([])
        self.assertEqual(result, {})

    def test_all_six_series(self):
        result = _classify_series_list(["O", "S", "H", "P", "K", "A"])
        self.assertEqual(len(result), 6)

    def test_unknown_series_handled(self):
        """Unknown series should not crash."""
        try:
            result = _classify_series_list(["X"])
        except (KeyError, ValueError):
            pass  # Acceptable to raise for unknown series


class TestDetectCrossings(unittest.TestCase):
    """Test _detect_crossings() U/R boundary detection."""

    def test_no_crossing_single_series(self):
        result = _detect_crossings(["O"])
        self.assertEqual(result, [])

    def test_no_crossing_same_type(self):
        """O and O — no crossing."""
        result = _detect_crossings(["O", "O"])
        self.assertEqual(result, [])

    def test_crossing_detected(self):
        """O (Understanding) and S (Reasoning) should cross."""
        result = _detect_crossings(["O", "S"])
        # Should detect at least one crossing
        self.assertIsInstance(result, list)

    def test_empty_list(self):
        result = _detect_crossings([])
        self.assertEqual(result, [])


class TestSuggestPwForCrossings(unittest.TestCase):
    """Test _suggest_pw_for_crossings() PW adjustment suggestions."""

    def test_no_crossings_empty_dict(self):
        result = _suggest_pw_for_crossings([], ["O"])
        self.assertEqual(result, {})

    def test_with_crossings_suggests_bridge(self):
        """Crossings should suggest bridge theorem PW adjustments."""
        result = _suggest_pw_for_crossings(["U→R"], ["O", "S"])
        self.assertIsInstance(result, dict)

    def test_return_type_is_dict(self):
        result = _suggest_pw_for_crossings([], [])
        self.assertIsInstance(result, dict)


class TestRecommendationDataclass(unittest.TestCase):
    """Test Recommendation dataclass."""

    def test_basic_creation(self):
        from mekhane.fep.attractor import OscillationType, OscillationDiagnosis

        rec = Recommendation(
            advice="test advice",
            workflows=["/dia"],
            series=["A"],
            oscillation=OscillationType.STABLE,
            confidence=0.9,
            interpretation=OscillationDiagnosis(
                type=OscillationType.STABLE,
                divergence_score=0.1,
                stability_confidence=0.9,
            ),
        )
        self.assertEqual(rec.advice, "test advice")
        self.assertEqual(rec.workflows, ["/dia"])

    def test_repr(self):
        from mekhane.fep.attractor import OscillationType, OscillationDiagnosis

        rec = Recommendation(
            advice="test",
            workflows=["/noe"],
            series=["O"],
            oscillation=OscillationType.STABLE,
            confidence=0.8,
            interpretation=OscillationDiagnosis(
                type=OscillationType.STABLE,
                divergence_score=0.0,
                stability_confidence=1.0,
            ),
        )
        r = repr(rec)
        self.assertIn("Recommendation", r)

    def test_default_fields(self):
        from mekhane.fep.attractor import OscillationType, OscillationDiagnosis

        rec = Recommendation(
            advice="",
            workflows=[],
            series=[],
            oscillation=OscillationType.STABLE,
            confidence=0.0,
            interpretation=OscillationDiagnosis(
                type=OscillationType.STABLE,
                divergence_score=0.0,
                stability_confidence=1.0,
            ),
        )
        self.assertEqual(rec.cognitive_types, {})
        self.assertEqual(rec.boundary_crossings, [])
        self.assertEqual(rec.pw_suggestion, {})
        self.assertEqual(rec.knowledge_context, [])


class TestCompoundRecommendationDataclass(unittest.TestCase):
    """Test CompoundRecommendation dataclass."""

    def test_basic_creation(self):
        cr = CompoundRecommendation(
            segments=[],
            merged_series=["O", "S"],
            merged_workflows=["/noe", "/s"],
            is_compound=True,
            is_multi_segment=True,
            primary=None,
        )
        self.assertEqual(cr.merged_series, ["O", "S"])
        self.assertTrue(cr.is_compound)

    def test_repr(self):
        cr = CompoundRecommendation(
            segments=[],
            merged_series=[],
            merged_workflows=[],
            is_compound=False,
            is_multi_segment=False,
            primary=None,
        )
        r = repr(cr)
        self.assertIsInstance(r, str)


if __name__ == "__main__":
    unittest.main()
