import sys
import unittest
from unittest.mock import MagicMock, patch, ANY

# =============================================================================
# Mocks setup (Must be before imports)
# =============================================================================

# Mock numpy
mock_numpy = MagicMock()
# Setup behavior for common numpy operations to avoid crashes
mock_numpy.zeros.return_value = MagicMock()
mock_numpy.ones.return_value = MagicMock()
mock_numpy.array.return_value = MagicMock()
# Support division for normalization
mock_numpy.ones.return_value.__truediv__.return_value = MagicMock()
sys.modules["numpy"] = mock_numpy

# Mock pymdp
mock_pymdp = MagicMock()
sys.modules["pymdp"] = mock_pymdp
sys.modules["pymdp.agent"] = MagicMock()
sys.modules["pymdp.utils"] = MagicMock()

# Mock yaml
mock_yaml = MagicMock()
sys.modules["yaml"] = mock_yaml

# Now import modules under test
from mekhane.fep.derivative_selector import (
    update_derivative_selector,
    select_derivative,
    DerivativeFEPManager,
    DerivativeRecommendation
)
from mekhane.fep.fep_agent import HegemonikónFEPAgent

class TestDerivativeFEPIntegration(unittest.TestCase):
    def setUp(self):
        # Reset agents cache before each test
        DerivativeFEPManager._agents = {}

    @patch("mekhane.fep.fep_agent.Agent")
    def test_update_derivative_selector_success(self, mock_pymdp_agent_cls):
        """Test that update_derivative_selector performs learning on success."""

        # Setup mocks
        mock_pymdp_agent_instance = mock_pymdp_agent_cls.return_value
        # Mock beliefs to be an array-like object
        mock_beliefs = MagicMock()
        mock_pymdp_agent_instance.infer_states.return_value = [mock_beliefs]

        # We need to spy on HegemonikónFEPAgent.update_A_dirichlet
        # Since DerivativeFEPManager creates instances internally, we can patch the class
        with patch.object(HegemonikónFEPAgent, 'update_A_dirichlet') as mock_update_A, \
             patch.object(HegemonikónFEPAgent, 'save_learned_A') as mock_save_A, \
             patch("mekhane.fep.derivative_selector.Path") as mock_path:

            # Execute
            update_derivative_selector(
                theorem="O1",
                derivative="nous",
                problem_context="本質的な問題",
                success=True
            )

            # Verify agent was created
            self.assertIn("O1", DerivativeFEPManager._agents)

            # Verify update_A_dirichlet was called
            # We don't care about the exact observation index (it depends on encoding), but it should be called
            mock_update_A.assert_called_once()

            # Verify save was called
            mock_save_A.assert_called_once()

    @patch("mekhane.fep.fep_agent.Agent")
    def test_update_derivative_selector_failure_no_update(self, mock_pymdp_agent_cls):
        """Test that failure does not trigger learning."""

        with patch.object(HegemonikónFEPAgent, 'update_A_dirichlet') as mock_update_A:
            update_derivative_selector(
                theorem="O1",
                derivative="nous",
                problem_context="test",
                success=False
            )

            mock_update_A.assert_not_called()

    @patch("mekhane.fep.fep_agent.Agent")
    def test_select_derivative_uses_fep(self, mock_pymdp_agent_cls):
        """Test that select_derivative uses FEP agent when enabled."""

        # Mock the agent to return high confidence for a specific derivative
        # O1 derivatives: ["nous", "phro", "meta"]
        # We want "meta" (index 2) to be selected

        with patch.object(HegemonikónFEPAgent, 'infer_states') as mock_infer:
            # beliefs[2] = 0.9 (high confidence)
            # We need to simulate the return value of infer_states
            # It returns {"beliefs": ...}

            # Since numpy is mocked, argmax logic in select_derivative relies on mock_numpy.argmax
            # We need to control what argmax returns.
            # And we need to control what float(beliefs[best_idx]) returns.

            mock_beliefs = MagicMock()
            mock_result = {"beliefs": mock_beliefs}
            mock_infer.return_value = mock_result

            # Setup numpy argmax to return 2 (meta)
            mock_numpy.argmax.return_value = 2

            # Setup beliefs access
            # float(beliefs[2]) -> 0.9
            # This is hard because beliefs is a MagicMock.
            # We can rely on __getitem__.
            mock_beliefs.__getitem__.return_value = 0.9

            # Also we need len(beliefs) to match len(derivs) which is 3
            mock_beliefs.__len__.return_value = 3

            # Execute
            result = select_derivative(
                theorem="O1",
                problem_context="neutral context",
                use_fep=True,
                use_llm_fallback=False # Disable LLM to isolate FEP
            )

            # Verify FEP was used
            mock_infer.assert_called()

            # Verify result
            # It should be "meta" because 0.9 confidence > keyword confidence (likely 0.5 for neutral)
            self.assertEqual(result.derivative, "meta")
            self.assertIn("FEP Inference", result.rationale)
            self.assertAlmostEqual(result.confidence, 0.9)

    def test_fep_manager_initialization(self):
        """Test that FEP Manager initializes agents correctly."""
        with patch("mekhane.fep.fep_agent.Agent"):
            agent = DerivativeFEPManager.get_agent("O1")
            self.assertIsInstance(agent, HegemonikónFEPAgent)
            self.assertEqual(agent.state_dim, 3)
            # Check cache
            self.assertIs(DerivativeFEPManager.get_agent("O1"), agent)

if __name__ == "__main__":
    unittest.main()
