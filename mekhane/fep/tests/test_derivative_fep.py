# PROOF: [L2/テスト] <- mekhane/fep/tests/
"""
Tests for DerivativeFEPAgent integration in derivative_selector.py.
"""
import pytest
import tempfile
import numpy as np
from pathlib import Path
from typing import Tuple, Dict

from mekhane.fep.derivative_selector import (
    DerivativeFEPAgent,
    _apply_fep_prior,
    update_derivative_selector,
    select_derivative,
    DerivativeRecommendation
)
from mekhane.fep.encoding import encode_input


# PURPOSE: Test initialization and defaults of DerivativeFEPAgent.
def test_derivative_fep_agent_init():
    """Verify initialization and defaults of DerivativeFEPAgent."""
    agent = DerivativeFEPAgent("O1")
    assert agent.theorem == "O1"
    assert agent.num_states == 3
    assert agent.num_obs == 18
    assert agent.pA.shape == (18, 3)
    np.testing.assert_allclose(agent._get_A().sum(axis=0), 1.0, atol=1e-10)


# PURPOSE: Test obs_to_index mapping logic.
def test_obs_to_index():
    """Verify observation index calculation."""
    agent = DerivativeFEPAgent("O1")
    # context(0-1) * 9 + urgency(0-2) * 3 + conf(0-2)
    assert agent._obs_to_index((0, 0, 0)) == 0
    assert agent._obs_to_index((1, 0, 0)) == 9
    assert agent._obs_to_index((1, 2, 2)) == 1 * 9 + 2 * 3 + 2  # 9 + 6 + 2 = 17


# PURPOSE: Test update_A_dirichlet logic and persistence.
def test_update_A_dirichlet():
    """Verify Dirichlet learning updates and saves the pA matrix correctly."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "test_pA.npy"
        agent = DerivativeFEPAgent("O1")
        agent.pA_path = path

        obs_tuple = (1, 1, 1)  # mid values
        deriv = "nous"

        # initial prior for the observation
        obs_idx = agent._obs_to_index(obs_tuple)
        A = agent._get_A()
        initial_prob = A[obs_idx, agent.derivatives.index(deriv)]

        agent.update_A_dirichlet(obs_tuple, deriv)

        # Prob should increase due to positive Dirichlet learning
        A_new = agent._get_A()
        new_prob = A_new[obs_idx, agent.derivatives.index(deriv)]
        assert new_prob > initial_prob

        # Verify saving
        assert path.exists()

        # Load fresh agent
        agent2 = DerivativeFEPAgent("O1")
        agent2.pA_path = path
        agent2.pA = agent2._load_or_init_pA()

        # Verify persistence
        np.testing.assert_allclose(agent.pA, agent2.pA)


# PURPOSE: Test FEP prior retrieval.
def test_get_derivative_prior():
    """Verify we can retrieve valid priors that sum to 1."""
    agent = DerivativeFEPAgent("O1")
    obs_tuple = (1, 0, 1)

    priors = agent.get_derivative_prior(obs_tuple)
    assert len(priors) == 3
    assert "nous" in priors
    assert "phro" in priors
    assert "meta" in priors

    # Should sum to 1
    total = sum(priors.values())
    assert abs(total - 1.0) < 1e-5


# PURPOSE: Test _apply_fep_prior behavior.
def test_apply_fep_prior():
    """Verify FEP prior boosts and penalizes confidence."""
    # We must patch the path or inject a mock A matrix for testing.
    agent = DerivativeFEPAgent("O1")

    # Let's say we learned heavily towards "nous" for a certain observation
    obs_tuple = encode_input("原理的なこと")
    obs_idx = agent._obs_to_index(obs_tuple)

    # manually bias pA matrix towards nous
    agent.pA[obs_idx, :] = [8.0, 1.0, 1.0]

    rec = DerivativeRecommendation(
        theorem="O1",
        derivative="nous",
        confidence=0.5,
        rationale="test",
        alternatives=["phro", "meta"]
    )

    # We will temporarily replace DerivativeFEPAgent._load_or_init_pA with a lambda
    # to return our biased matrix in _apply_fep_prior, or just mock it.
    original_init = DerivativeFEPAgent._load_or_init_pA
    DerivativeFEPAgent._load_or_init_pA = lambda self: agent.pA

    try:
        updated_rec = _apply_fep_prior(rec, "原理的なこと")
        assert updated_rec.confidence > 0.5
        assert "FEP boost" in updated_rec.rationale
    finally:
        DerivativeFEPAgent._load_or_init_pA = original_init


# PURPOSE: Test the end-to-end integration API update_derivative_selector.
def test_update_derivative_selector():
    """Verify we can call update_derivative_selector without crashing."""
    original_init = DerivativeFEPAgent._load_or_init_pA
    try:
        DerivativeFEPAgent._load_or_init_pA = lambda self: np.ones((18, 3))
        # Should not throw any errors
        update_derivative_selector("O1", "nous", "原理", success=True)
        # Should early return
        update_derivative_selector("O1", "nous", "原理", success=False)
    finally:
        DerivativeFEPAgent._load_or_init_pA = original_init


# PURPOSE: Test select_derivative using the use_fep flag.
def test_select_derivative_with_fep():
    """Verify select_derivative can use FEP prior adjustment."""
    result = select_derivative("O1", "本質", use_fep=True)
    assert result.theorem == "O1"
