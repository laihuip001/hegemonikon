import pytest
import numpy as np
import os
from pathlib import Path
from mekhane.fep.fep_agent import DerivativeFEPAgent
from mekhane.fep.derivative_selector import (
    select_derivative,
    update_derivative_selector,
    get_derivative_agent,
    encode_observation_for_fep,
    _DERIVATIVE_AGENTS,
    list_derivatives
)

# Mock persistence path to avoid messing with real data
@pytest.fixture
def mock_persistence(monkeypatch, tmp_path):
    d = tmp_path / ".hegemonikon"
    d.mkdir()
    fake_path = d / "learned_A.npy"

    # We need to patch LEARNED_A_PATH in persistence module
    # But it is imported in derivative_selector functions locally.
    # We can patch mekhane.fep.persistence.LEARNED_A_PATH
    import mekhane.fep.persistence
    monkeypatch.setattr(mekhane.fep.persistence, "LEARNED_A_PATH", fake_path)
    return d

def test_derivative_fep_agent_init():
    try:
        agent = DerivativeFEPAgent(state_dim=3, obs_dim=4)
        assert agent.state_dim == 3
        assert agent.obs_dim == 4
        # Accessing A via pymdp agent structure
        # A can be object array or list
        if isinstance(agent.agent.A, np.ndarray) and agent.agent.A.dtype == object:
             assert agent.agent.A[0].shape == (4, 3)
        elif isinstance(agent.agent.A, list):
             assert agent.agent.A[0].shape == (4, 3)
        else:
             assert agent.agent.A.shape == (4, 3)
    except ImportError:
        pytest.skip("pymdp not installed")

def test_encode_observation_for_fep():
    # Test with O1 patterns
    # "nous": ["本質", "原理"...]
    # derivatives = ["nous", "phro", "meta"] -> indices 0, 1, 2

    text_nous = "この問題の本質は何か？"
    obs_nous = encode_observation_for_fep(text_nous, "O1")
    assert obs_nous == 0

    text_none = "何も関係ないテキストxyz123"
    obs_none = encode_observation_for_fep(text_none, "O1")
    # None is index 3 (len=3)
    assert obs_none == 3

def test_learning_flow(mock_persistence):
    theorem = "O1"
    # Ensure clean state
    if theorem in _DERIVATIVE_AGENTS:
        del _DERIVATIVE_AGENTS[theorem]

    try:
        # 1. Initial selection
        agent = get_derivative_agent(theorem)
        if agent is None:
             pytest.skip("Agent not initialized (pymdp missing?)")

        assert agent is not None

        # Initial beliefs should be uniform
        text = "この問題の本質は何か？"
        obs_idx = encode_observation_for_fep(text, theorem) # 0 (nous)
        beliefs = agent.infer_states(obs_idx)
        # Uniform: [0.33, 0.33, 0.33]
        assert np.allclose(beliefs, [1/3, 1/3, 1/3])

        # 2. Update with feedback
        # Reinforce "nous" (index 0)
        update_derivative_selector(theorem, "nous", text, success=True)

        # 3. Check beliefs again
        beliefs_new = agent.infer_states(obs_idx)
        assert beliefs_new[0] > 1/3
        assert beliefs_new[0] > beliefs_new[1]

        # 4. Persistence check
        expected_path = mock_persistence / "learned_A_O1.npy"
        assert expected_path.exists()

        # 5. Reload agent
        del _DERIVATIVE_AGENTS[theorem]
        agent2 = get_derivative_agent(theorem)
        beliefs_reloaded = agent2.infer_states(obs_idx)
        assert np.allclose(beliefs_new, beliefs_reloaded)

    except ImportError:
        pytest.skip("pymdp not installed")

def test_select_derivative_integration(mock_persistence):
    theorem = "O1"
    if theorem in _DERIVATIVE_AGENTS:
        del _DERIVATIVE_AGENTS[theorem]

    try:
        text = "この問題の本質は何か？" # Maps to nous (idx 0)

        # Initially FEP is uniform, so select_derivative returns keyword result
        res = select_derivative(theorem, text, use_fep=True)
        # Assuming keyword match works and gives > 0.5 confidence, FEP (0.33) won't override unless threshold is low.
        # Threshold is ~0.43. 0.33 < 0.43. So FEP ignored.
        assert "FEP" not in res.rationale

        # Train heavily to boost confidence
        for _ in range(10):
            update_derivative_selector(theorem, "nous", text, success=True)

        # Now FEP confidence should be high
        agent = get_derivative_agent(theorem)
        obs = encode_observation_for_fep(text, theorem)
        beliefs = agent.infer_states(obs)

        # Confidence should be high
        if beliefs[0] > 0.45:
            res_fep = select_derivative(theorem, text, use_fep=True)
            assert "FEP" in res_fep.rationale
            assert res_fep.derivative == "nous"

    except ImportError:
        pytest.skip("pymdp not installed")
