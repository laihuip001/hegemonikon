
import pytest
import numpy as np
from unittest.mock import MagicMock, patch, ANY
from mekhane.fep.derivative_selector import (
    DerivativeFEPAgent,
    update_derivative_selector,
    select_derivative
)

class TestDerivativeFEPAgent:
    def test_init(self):
        agent = DerivativeFEPAgent("O1", ["nous", "phro", "meta"])
        assert agent.state_dim == 3
        assert agent.obs_dims == {"pattern_match": 3}
        # Check A matrix shape (pymdp stores it as object array or list usually)
        A = agent.agent.A
        if isinstance(A, np.ndarray) and A.dtype == object:
            A_matrix = A[0]
        elif isinstance(A, list):
            A_matrix = A[0]
        else:
            A_matrix = A
        assert A_matrix.shape == (3, 3)

    def test_default_A_is_identity_like(self):
        agent = DerivativeFEPAgent("O1", ["A", "B"])
        A = agent.agent.A
        if isinstance(A, np.ndarray) and A.dtype == object:
            A_matrix = A[0]
        elif isinstance(A, list):
            A_matrix = A[0]
        else:
            A_matrix = A

        # Check diagonals are high
        assert A_matrix[0, 0] > 0.5
        assert A_matrix[1, 1] > 0.5
        # Check normalization
        assert np.allclose(A_matrix.sum(axis=0), 1.0)

    def test_index_to_state_names(self):
        agent = DerivativeFEPAgent("O1", ["A", "B"])
        names = agent._index_to_state_names(0)
        assert names["derivative"] == "A"
        names_unknown = agent._index_to_state_names(99)
        assert names_unknown["derivative"] == "unknown"

@patch("mekhane.fep.derivative_selector.DerivativeFEPAgent")
def test_update_derivative_selector_success(MockAgent):
    """Test successful update flow."""
    # Setup mock agent
    mock_instance = MockAgent.return_value
    mock_instance.state_dim = 3

    # Run update
    # Context "本質" strongly matches 'nous' (index 0)
    # We say 'nous' was successful (state index 0)
    update_derivative_selector(
        theorem="O1",
        derivative="nous",
        problem_context="これは本質的な問題です",
        success=True
    )

    # Verify agent was initialized with correct derivatives
    args, kwargs = MockAgent.call_args
    assert kwargs['theorem'] == "O1"
    assert "nous" in kwargs['derivatives']

    # Verify load was called
    mock_instance.load_learned_A.assert_called()

    # Verify update_A_dirichlet was called with correct observation
    # 'nous' is 1st in O1 list -> index 0
    mock_instance.update_A_dirichlet.assert_called_with(observation=0)

    # Verify save was called
    mock_instance.save_learned_A.assert_called()

@patch("mekhane.fep.derivative_selector.DerivativeFEPAgent")
def test_update_derivative_selector_failure(MockAgent):
    """Test ignored failure."""
    update_derivative_selector(
        theorem="O1",
        derivative="nous",
        problem_context="foo",
        success=False
    )

    MockAgent.assert_not_called()

@patch("mekhane.fep.derivative_selector.DerivativeFEPAgent")
def test_update_derivative_selector_unknown_theorem(MockAgent):
    """Test unknown theorem."""
    update_derivative_selector(
        theorem="ZZ",
        derivative="nous",
        problem_context="foo",
        success=True
    )

    MockAgent.assert_not_called()
