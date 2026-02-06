import sys
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

# Mock pymdp before importing anything that uses it
sys.modules["pymdp"] = MagicMock()
sys.modules["pymdp.agent"] = MagicMock()
sys.modules["pymdp.utils"] = MagicMock()

# Mock Agent class
class MockAgent:
    def __init__(self, A=None, B=None, C=None, D=None, **kwargs):
        self.A = A
        self.B = B
        self.C = C
        self.D = D

sys.modules["pymdp.agent"].Agent = MockAgent

# Import modules under test
# This must happen AFTER mocking pymdp
from mekhane.fep.derivative_selector import (
    DerivativeFEPAgent,
    update_derivative_selector,
)
import mekhane.fep.derivative_selector as ds
from mekhane.fep import fep_agent

@pytest.fixture
def mock_persistence(tmp_path):
    with patch("mekhane.fep.derivative_selector.DERIVATIVE_FEP_PATH", tmp_path), \
         patch("mekhane.fep.derivative_selector.DerivativeFEPAgent.load_learned_A") as mock_load, \
         patch("mekhane.fep.derivative_selector.DerivativeFEPAgent.save_learned_A") as mock_save:
        yield mock_load, mock_save

def test_derivative_fep_agent_init():
    # Force PYMDP_AVAILABLE to True for this test
    ds.PYMDP_AVAILABLE = True
    fep_agent.PYMDP_AVAILABLE = True
    fep_agent.Agent = MockAgent

    agent = DerivativeFEPAgent("O1")
    assert agent.theorem == "O1"
    # O1 has 3 derivatives: nous, phro, meta
    assert agent.state_dim == 3
    # A should be list of 3 matrices (abstraction, context, reflection)
    assert isinstance(agent.agent.A, list)
    assert len(agent.agent.A) == 3
    # Each matrix should be (3, 3) (3 obs levels, 3 states)
    assert agent.agent.A[0].shape == (3, 3)

    # B should be identity-like
    assert agent.agent.B.shape == (3, 3, 1)
    assert np.allclose(agent.agent.B[:, :, 0], np.eye(3))

def test_update_a_dirichlet():
    ds.PYMDP_AVAILABLE = True
    fep_agent.PYMDP_AVAILABLE = True
    fep_agent.Agent = MockAgent
    agent = DerivativeFEPAgent("O1")

    # Set beliefs to be peaked at state 0 (nous)
    agent.beliefs = np.array([1.0, 0.0, 0.0])

    # Capture initial A[0]
    initial_A0 = agent.agent.A[0].copy()

    # Observation: (0, 0, 0)
    # abstraction=0, context=0, reflection=0
    obs = (0, 0, 0)

    agent.update_A_dirichlet(obs, learning_rate=1.0)

    # A[0] should be updated
    # pA += 1.0 * outer([1,0,0], [1,0,0]) = [[1,0,0], ...]
    # So A[0][0,0] increases.
    assert not np.array_equal(agent.agent.A[0], initial_A0)
    assert agent.agent.A[0][0, 0] > initial_A0[0, 0]

    # A[1] should also be updated
    assert not np.array_equal(agent.agent.A[1], initial_A0)

def test_update_derivative_selector_success(mock_persistence):
    mock_load, mock_save = mock_persistence
    ds.PYMDP_AVAILABLE = True
    fep_agent.PYMDP_AVAILABLE = True
    fep_agent.Agent = MockAgent

    # "nous" keywords -> abstract problem
    context = "この概念の本質は何か"

    update_derivative_selector("O1", "nous", context, success=True)

    mock_load.assert_called_once()
    mock_save.assert_called_once()

def test_update_derivative_selector_failure(mock_persistence):
    mock_load, mock_save = mock_persistence
    ds.PYMDP_AVAILABLE = True
    fep_agent.PYMDP_AVAILABLE = True
    fep_agent.Agent = MockAgent

    update_derivative_selector("O1", "nous", "test", success=False)

    mock_load.assert_not_called()
    mock_save.assert_not_called()

def test_update_derivative_selector_unknown_derivative(mock_persistence):
    mock_load, mock_save = mock_persistence
    ds.PYMDP_AVAILABLE = True
    fep_agent.PYMDP_AVAILABLE = True
    fep_agent.Agent = MockAgent

    update_derivative_selector("O1", "unknown_deriv", "test", success=True)

    mock_load.assert_not_called()
    mock_save.assert_not_called()

def test_update_derivative_selector_no_pymdp(mock_persistence):
    mock_load, mock_save = mock_persistence

    # Simulate pymdp not available
    original_flag = ds.PYMDP_AVAILABLE
    ds.PYMDP_AVAILABLE = False

    try:
        update_derivative_selector("O1", "nous", "test", success=True)

        mock_load.assert_not_called()
        mock_save.assert_not_called()
    finally:
        ds.PYMDP_AVAILABLE = original_flag
