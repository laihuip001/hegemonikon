"""Tests for mekhane.fep.encoding — FEP encoding helpers."""

import unittest
from mekhane.fep.encoding import encode_boulesis_output, encode_noesis_output


class TestEncodeBoulesis(unittest.TestCase):
    """Test encode_boulesis_output() mapping."""

    def test_returns_tuple_of_3(self):
        obs = encode_boulesis_output(impulse_score=50, feasibility_score=50)
        self.assertIsInstance(obs, tuple)
        self.assertEqual(len(obs), 3)

    def test_all_elements_are_ints(self):
        obs = encode_boulesis_output(impulse_score=50, feasibility_score=50)
        for v in obs:
            self.assertIsInstance(v, int)

    def test_high_impulse_high_urgency(self):
        """impulse >= 70 → high urgency → urgency_idx should be higher."""
        high = encode_boulesis_output(impulse_score=80, feasibility_score=50)
        low = encode_boulesis_output(impulse_score=10, feasibility_score=50)
        # urgency is index 1; high impulse → higher urgency index
        self.assertGreaterEqual(high[1], low[1])

    def test_low_impulse_low_urgency(self):
        obs = encode_boulesis_output(impulse_score=10, feasibility_score=50)
        # urgency_idx = 0 for low urgency
        self.assertEqual(obs[1], 0)

    def test_high_feasibility_clear_context(self):
        """feasibility >= 50 → clear context → context_idx = 1."""
        obs = encode_boulesis_output(impulse_score=30, feasibility_score=80)
        self.assertEqual(obs[0], 1)  # clear context

    def test_low_feasibility_ambiguous_context(self):
        """feasibility < 50 → ambiguous context → context_idx = 0."""
        obs = encode_boulesis_output(impulse_score=30, feasibility_score=20)
        self.assertEqual(obs[0], 0)  # ambiguous context

    def test_high_feasibility_high_confidence(self):
        """feasibility >= 70 → high confidence → confidence_idx = 2."""
        obs = encode_boulesis_output(impulse_score=30, feasibility_score=80)
        self.assertEqual(obs[2], 2)  # high confidence

    def test_medium_feasibility_medium_confidence(self):
        """40 <= feasibility < 70 → medium confidence → confidence_idx = 1."""
        obs = encode_boulesis_output(impulse_score=30, feasibility_score=55)
        self.assertEqual(obs[2], 1)  # medium confidence

    def test_low_feasibility_low_confidence(self):
        """feasibility < 40 → low confidence → confidence_idx = 0."""
        obs = encode_boulesis_output(impulse_score=30, feasibility_score=20)
        self.assertEqual(obs[2], 0)  # low confidence

    def test_boundary_impulse_70(self):
        obs = encode_boulesis_output(impulse_score=70, feasibility_score=50)
        self.assertEqual(obs[1], 2)  # high urgency

    def test_boundary_impulse_40(self):
        obs = encode_boulesis_output(impulse_score=40, feasibility_score=50)
        self.assertEqual(obs[1], 1)  # medium urgency

    def test_boundary_feasibility_50(self):
        obs = encode_boulesis_output(impulse_score=30, feasibility_score=50)
        self.assertEqual(obs[0], 1)  # clear (>= 50)

    def test_boundary_feasibility_49(self):
        obs = encode_boulesis_output(impulse_score=30, feasibility_score=49)
        self.assertEqual(obs[0], 0)  # ambiguous (< 50)


class TestEncodeNoesis(unittest.TestCase):
    """Test encode_noesis_output() mapping."""

    def test_returns_tuple_of_3(self):
        obs = encode_noesis_output(confidence_score=0.5, uncertainty_zones=[])
        self.assertIsInstance(obs, tuple)
        self.assertEqual(len(obs), 3)

    def test_no_uncertainty_zones_clear_context(self):
        obs = encode_noesis_output(confidence_score=0.5, uncertainty_zones=[])
        self.assertEqual(obs[0], 1)  # clear context

    def test_many_uncertainty_zones_ambiguous(self):
        zones = [{"zone": f"z{i}", "doubt_score": 0.5} for i in range(5)]
        obs = encode_noesis_output(confidence_score=0.5, uncertainty_zones=zones)
        self.assertEqual(obs[0], 0)  # ambiguous context

    def test_always_low_urgency(self):
        """Noesis is deliberative → urgency always low."""
        obs = encode_noesis_output(confidence_score=0.9, uncertainty_zones=[])
        self.assertEqual(obs[1], 0)  # low urgency

    def test_high_confidence(self):
        obs = encode_noesis_output(confidence_score=0.9, uncertainty_zones=[])
        self.assertEqual(obs[2], 2)  # high confidence

    def test_low_confidence(self):
        obs = encode_noesis_output(confidence_score=0.2, uncertainty_zones=[])
        self.assertEqual(obs[2], 0)  # low confidence


if __name__ == "__main__":
    unittest.main()
