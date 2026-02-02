import unittest
from unittest.mock import MagicMock, patch
import sys
import numpy as np
import tempfile
import shutil
from pathlib import Path
import os

# Mock pymdp before importing fep_agent
mock_pymdp = MagicMock()
mock_agent_module = MagicMock()
mock_agent_class = MagicMock()

# Configure mock Agent instance
mock_agent_instance = MagicMock()
# Mock A matrix on instance (as array)
mock_agent_instance.A = np.zeros((27, 3))
# Mock infer_states to return something usable by default (uniform)
mock_agent_instance.infer_states.return_value = np.array([0.33, 0.33, 0.34])

mock_agent_class.return_value = mock_agent_instance

mock_agent_module.Agent = mock_agent_class
sys.modules['pymdp'] = mock_pymdp
sys.modules['pymdp.agent'] = mock_agent_module
sys.modules['pymdp.utils'] = MagicMock()

# Now import modules to test
from mekhane.fep.derivative_selector import (
    update_derivative_selector,
    select_derivative,
    _get_derivative_agent,
    DERIVATIVE_OBSERVATION_DIM,
    encode_for_derivative_selection,
    _flatten_derivative_observation
)
from mekhane.fep.fep_agent import HegemonikónFEPAgent

class TestDerivativeFEP(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for persistence
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir) / ".hegemonikon/learned_A.npy"
        self.log_path = Path(self.test_dir) / ".hegemonikon/derivative_selections.yaml"

        # Mock paths in multiple places
        self.patchers = [
            patch('mekhane.fep.derivative_selector.LEARNED_A_PATH', self.test_path),
            patch('mekhane.fep.derivative_selector.SELECTION_LOG_PATH', self.log_path),
            patch('mekhane.fep.persistence.LEARNED_A_PATH', self.test_path),
        ]

        for p in self.patchers:
            p.start()

    def tearDown(self):
        for p in self.patchers:
            p.stop()
        shutil.rmtree(self.test_dir)

    def test_encoding(self):
        obs = encode_for_derivative_selection("本質的な問題", "O1")
        self.assertEqual(obs, (2, 0, 0))
        flat = _flatten_derivative_observation(obs)
        self.assertEqual(flat, 18)

    def test_agent_creation(self):
        """Test that we can create an agent for O1."""
        agent = _get_derivative_agent("O1")

        self.assertIsNotNone(agent)
        self.assertIsInstance(agent, HegemonikónFEPAgent)
        self.assertEqual(agent.state_dim, 3)
        self.assertEqual(agent.obs_dims["derivative_context"], 27)
        self.assertEqual(agent.agent, mock_agent_instance)

    def test_update_selector(self):
        """Test updating the selector."""
        initial_A = np.zeros((27, 3))
        initial_A[18, 0] = 0.1
        mock_agent_instance.A = initial_A.copy()

        update_derivative_selector("O1", "nous", "本質的な問題", success=True)

        final_A = mock_agent_instance.A

        deriv_path = self.test_path.parent / "derivatives/O1_A.npy"
        self.assertTrue(deriv_path.exists())

        self.assertGreater(final_A[18, 0], 0.1)

    def test_select_using_fep(self):
        """Test that selection uses FEP if available."""
        # 1. Simulate weak keyword match ("neutral input" -> usually defaults to something with ~0.5 confidence)
        # 2. Simulate STRONG FEP belief for "nous" (index 0)

        # Set mock return value for infer_states to favor state 0 (nous)
        # 3 states: nous, phro, meta
        mock_agent_instance.infer_states.return_value = np.array([0.9, 0.05, 0.05])

        # Call select_derivative
        # encode_for_derivative_selection("neutral") -> likely (0,0,0) -> obs 0
        # infer_states called with 0 -> returns [0.9, ...]
        # FEP confidence = 0.9
        # Keyword confidence < 0.9 (usually 0.5)
        # Should pick nous

        result = select_derivative("O1", "neutral input", use_fep=True)

        self.assertEqual(result.derivative, "nous")
        self.assertIn("FEP Agent", result.rationale)
        self.assertAlmostEqual(result.confidence, 0.9)

if __name__ == '__main__':
    unittest.main()
