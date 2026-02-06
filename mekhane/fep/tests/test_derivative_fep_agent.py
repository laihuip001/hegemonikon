import os
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import patch, PropertyMock

from mekhane.fep.derivative_selector import (
    DerivativeFEPAgent,
    update_derivative_selector,
    encode_for_derivative_selection,
    list_derivatives,
)

class TestDerivativeFEPAgent:
    """Test suite for DerivativeFEPAgent."""

    @pytest.fixture
    def temp_hegemonikon_dir(self, tmp_path):
        """Fixture to provide a temporary directory for persistence."""
        d = tmp_path / ".hegemonikon"
        d.mkdir()
        return d

    def test_instantiation(self):
        """Test agent can be instantiated."""
        agent = DerivativeFEPAgent("O1")
        assert agent.state_dim == 3
        assert agent.obs_dims == {"context": 27}

        # Check matrices dimensions (wrapped in object array)
        A = agent.agent.A
        if isinstance(A, np.ndarray) and A.dtype == object:
            A = A[0]
        assert A.shape == (27, 3)

        B = agent.agent.B
        if isinstance(B, np.ndarray) and B.dtype == object:
            B = B[0]
        assert B.shape == (3, 3, 1)

    def test_persistence_path_fallback(self, monkeypatch, tmp_path):
        """Test persistence path logic uses env var."""
        target_dir = tmp_path / "custom_hegemonikon"
        target_dir.mkdir()
        monkeypatch.setenv("HEGEMONIKON_DIR", str(target_dir))

        agent = DerivativeFEPAgent("O1")
        assert agent.persistence_path.parent == target_dir
        assert agent.persistence_path.name == "derivative_A_O1.npy"

    def test_update_derivative_selector_flow(self, temp_hegemonikon_dir, monkeypatch):
        """Test the full update flow with persistence."""
        # Force agent to use temp dir
        monkeypatch.setenv("HEGEMONIKON_DIR", str(temp_hegemonikon_dir))

        theorem = "O1"
        derivative = "nous"
        context = "本質的な原理を理解したい"

        # Get initial probability
        agent_pre = DerivativeFEPAgent(theorem)

        # Access inner A matrix safely
        A_pre = agent_pre.agent.A
        if isinstance(A_pre, np.ndarray) and A_pre.dtype == object:
             A_pre = A_pre[0]

        # Calculate indices
        obs_tuple = encode_for_derivative_selection(context, theorem)
        obs_idx = obs_tuple[0]*9 + obs_tuple[1]*3 + obs_tuple[2]
        state_idx = list_derivatives(theorem).index(derivative)

        initial_prob = A_pre[obs_idx, state_idx]

        # Run update
        update_derivative_selector(theorem, derivative, context, success=True)

        # Verify update persisted
        agent_post = DerivativeFEPAgent(theorem)
        loaded = agent_post.load_learned_A()
        assert loaded, "Should have loaded saved A matrix"

        A_post = agent_post.agent.A
        if isinstance(A_post, np.ndarray) and A_post.dtype == object:
             A_post = A_post[0]

        new_prob = A_post[obs_idx, state_idx]

        assert new_prob > initial_prob, "Probability of selected derivative given context should increase"

    def test_infer_states(self):
        """Test custom infer_states returns derivative names."""
        agent = DerivativeFEPAgent("O1")
        # Observation 0
        res = agent.infer_states(0)
        assert "map_state_names" in res
        assert "derivative" in res["map_state_names"]
        # With uniform prior and uniform A, any state is likely.
        # But we check that the name maps to a valid derivative
        deriv = res["map_state_names"]["derivative"]
        assert deriv in ["nous", "phro", "meta"]
