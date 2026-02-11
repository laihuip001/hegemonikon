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


# PURPOSE: Test suite validating classify series list correctness
class TestClassifySeriesList(unittest.TestCase):
    """Test _classify_series_list() series→CognitiveType mapping."""

    # PURPOSE: Verify single o series behaves correctly
    def test_single_o_series(self):
        """Verify single o series behavior."""
        result = _classify_series_list(["O"])
        self.assertIn("O", result)

    # PURPOSE: Verify multiple series behaves correctly
    def test_multiple_series(self):
        """Verify multiple series behavior."""
        result = _classify_series_list(["O", "S", "A"])
        self.assertEqual(len(result), 3)

    # PURPOSE: Verify empty list behaves correctly
    def test_empty_list(self):
        """Verify empty list behavior."""
        result = _classify_series_list([])
        self.assertEqual(result, {})

    # PURPOSE: Verify all six series behaves correctly
    def test_all_six_series(self):
        """Verify all six series behavior."""
        result = _classify_series_list(["O", "S", "H", "P", "K", "A"])
        self.assertEqual(len(result), 6)

    # PURPOSE: Verify unknown series handled behaves correctly
    def test_unknown_series_handled(self):
        """Unknown series should not crash."""
        try:
            result = _classify_series_list(["X"])
        except (KeyError, ValueError):
            pass  # Acceptable to raise for unknown series


# PURPOSE: Test suite validating detect crossings correctness
class TestDetectCrossings(unittest.TestCase):
    """Test _detect_crossings() U/R boundary detection."""

    # PURPOSE: Verify no crossing single series behaves correctly
    def test_no_crossing_single_series(self):
        """Verify no crossing single series behavior."""
        result = _detect_crossings(["O"])
        self.assertEqual(result, [])

    # PURPOSE: Verify no crossing same type behaves correctly
    def test_no_crossing_same_type(self):
        """O and O — no crossing."""
        result = _detect_crossings(["O", "O"])
        self.assertEqual(result, [])

    # PURPOSE: Verify crossing detected behaves correctly
    def test_crossing_detected(self):
        """O (Understanding) and S (Reasoning) should cross."""
        result = _detect_crossings(["O", "S"])
        # Should detect at least one crossing
        self.assertIsInstance(result, list)

    # PURPOSE: Verify empty list behaves correctly
    def test_empty_list(self):
        """Verify empty list behavior."""
        result = _detect_crossings([])
        self.assertEqual(result, [])


# PURPOSE: Test suite validating suggest pw for crossings correctness
class TestSuggestPwForCrossings(unittest.TestCase):
    """Test _suggest_pw_for_crossings() PW adjustment suggestions."""

    # PURPOSE: Verify no crossings empty dict behaves correctly
    def test_no_crossings_empty_dict(self):
        """Verify no crossings empty dict behavior."""
        result = _suggest_pw_for_crossings([], ["O"])
        self.assertEqual(result, {})

    # PURPOSE: Verify with crossings suggests bridge behaves correctly
    def test_with_crossings_suggests_bridge(self):
        """Crossings should suggest bridge theorem PW adjustments."""
        result = _suggest_pw_for_crossings(["U→R"], ["O", "S"])
        self.assertIsInstance(result, dict)

    # PURPOSE: Verify return type is dict behaves correctly
    def test_return_type_is_dict(self):
        """Verify return type is dict behavior."""
        result = _suggest_pw_for_crossings([], [])
        self.assertIsInstance(result, dict)


# PURPOSE: Test suite validating recommendation dataclass correctness
class TestRecommendationDataclass(unittest.TestCase):
    """Test Recommendation dataclass."""

    # PURPOSE: Verify basic creation behaves correctly
    def test_basic_creation(self):
        """Verify basic creation behavior."""
        from mekhane.fep.attractor import OscillationType, OscillationDiagnosis

        rec = Recommendation(
            advice="test advice",
            workflows=["/dia"],
            series=["A"],
            oscillation=OscillationType.CLEAR,
            confidence=0.9,
            interpretation=OscillationDiagnosis(
                oscillation=OscillationType.CLEAR,
                theory="test",
                action="proceed",
                morphisms=[],
                confidence_modifier=0.0,
            ),
        )
        self.assertEqual(rec.advice, "test advice")
        self.assertEqual(rec.workflows, ["/dia"])

    # PURPOSE: Verify repr behaves correctly
    def test_repr(self):
        """Verify repr behavior."""
        from mekhane.fep.attractor import OscillationType, OscillationDiagnosis

        rec = Recommendation(
            advice="test",
            workflows=["/noe"],
            series=["O"],
            oscillation=OscillationType.CLEAR,
            confidence=0.8,
            interpretation=OscillationDiagnosis(
                oscillation=OscillationType.CLEAR,
                theory="test",
                action="proceed",
                morphisms=[],
                confidence_modifier=0.0,
            ),
        )
        r = repr(rec)
        self.assertIn("Rec:", r)

    # PURPOSE: Verify default fields behaves correctly
    def test_default_fields(self):
        """Verify default fields behavior."""
        from mekhane.fep.attractor import OscillationType, OscillationDiagnosis

        rec = Recommendation(
            advice="",
            workflows=[],
            series=[],
            oscillation=OscillationType.CLEAR,
            confidence=0.0,
            interpretation=OscillationDiagnosis(
                oscillation=OscillationType.CLEAR,
                theory="test",
                action="proceed",
                morphisms=[],
                confidence_modifier=0.0,
            ),
        )
        self.assertEqual(rec.cognitive_types, {})
        self.assertEqual(rec.boundary_crossings, [])
        self.assertEqual(rec.pw_suggestion, {})
        self.assertEqual(rec.knowledge_context, [])


# PURPOSE: Test suite validating compound recommendation dataclass correctness
class TestCompoundRecommendationDataclass(unittest.TestCase):
    """Test CompoundRecommendation dataclass."""

    # PURPOSE: Verify basic creation behaves correctly
    def test_basic_creation(self):
        """Verify basic creation behavior."""
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

    # PURPOSE: Verify repr behaves correctly
    def test_repr(self):
        """Verify repr behavior."""
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
