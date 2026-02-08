# PROOF: [L2/テスト] <- mekhane/fep/tests/
# PURPOSE: FEP Agent v2 (48-state) の統合テスト
"""
Tests for HegemonikónFEPAgentV2 — 48-state model with Series integration.

Tests:
1. Matrix shapes (A=14×48, B=48×48×7, C=14, D=48)
2. State index round-trip
3. Topic observation influences Series selection
4. act_X transitions to Series X
5. Two-cycle learning changes A matrix
6. Observe action doesn't change Series
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest


class TestStateSpacesV2:
    """State space definition tests."""

    def test_dimensions(self):
        from mekhane.fep.state_spaces_v2 import NUM_STATES_V2, NUM_OBS_V2, NUM_ACTIONS_V2
        assert NUM_STATES_V2 == 48
        assert NUM_OBS_V2 == 14
        assert NUM_ACTIONS_V2 == 7

    def test_index_round_trip(self):
        from mekhane.fep.state_spaces_v2 import (
            state_to_index_v2, index_to_state_v2, NUM_STATES_V2,
        )
        for i in range(NUM_STATES_V2):
            p, a, h, s = index_to_state_v2(i)
            j = state_to_index_v2(p, a, h, s)
            assert i == j, f"Round-trip failed: {i} → ({p},{a},{h},{s}) → {j}"

    def test_all_series_covered(self):
        from mekhane.fep.state_spaces_v2 import (
            index_to_state_v2, NUM_STATES_V2, SERIES_STATES,
        )
        series_seen = set()
        for i in range(NUM_STATES_V2):
            _, _, _, s = index_to_state_v2(i)
            series_seen.add(s)
        assert series_seen == set(SERIES_STATES)


class TestFEPAgentV2:
    """48-state agent tests."""

    def test_matrix_shapes(self):
        from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
        agent = HegemonikónFEPAgentV2()

        A = agent._default_A()
        B = agent._default_B()
        C = agent._default_C()
        D = agent._default_D()

        assert A.shape == (14, 48), f"A shape: {A.shape}"
        assert B.shape == (48, 48, 7), f"B shape: {B.shape}"
        assert C.shape == (14,), f"C shape: {C.shape}"
        assert D.shape == (48,), f"D shape: {D.shape}"

    def test_A_columns_normalized(self):
        from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
        agent = HegemonikónFEPAgentV2()
        A = agent._default_A()
        col_sums = A.sum(axis=0)
        np.testing.assert_allclose(col_sums, 1.0, atol=1e-10)

    def test_B_columns_normalized(self):
        from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
        agent = HegemonikónFEPAgentV2()
        B = agent._default_B()
        for a in range(7):
            col_sums = B[:, :, a].sum(axis=0)
            np.testing.assert_allclose(col_sums, 1.0, atol=1e-10)

    def test_D_normalized(self):
        from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
        agent = HegemonikónFEPAgentV2()
        D = agent._default_D()
        assert abs(D.sum() - 1.0) < 1e-10

    def test_step_returns_series(self):
        """step() returns selected_series for act_X actions."""
        from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
        agent = HegemonikónFEPAgentV2()

        result = agent.step(observation=0)

        assert "action_name" in result
        assert "selected_series" in result
        assert result["action_name"] in [
            "observe", "act_O", "act_S", "act_H", "act_P", "act_K", "act_A",
        ]
        if result["action_name"] == "observe":
            assert result["selected_series"] is None
        else:
            assert result["selected_series"] in ["O", "S", "H", "P", "K", "A"]

    def test_step_returns_map_state_with_series(self):
        """MAP state includes series field."""
        from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
        agent = HegemonikónFEPAgentV2()

        result = agent.step(observation=0)
        names = result["map_state_names"]

        assert "phantasia" in names
        assert "assent" in names
        assert "horme" in names
        assert "series" in names
        assert names["series"] in ["O", "S", "H", "P", "K", "A"]

    def test_topic_observation_affects_beliefs(self):
        """Feeding topic=O observation should increase belief in O-series states."""
        from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
        from mekhane.fep.state_spaces_v2 import index_to_state_v2

        agent = HegemonikónFEPAgentV2()

        # Topic observation: O is at index 8 (context=2, urgency=3, conf=3, then topic starts)
        result = agent.step(observation=8)  # topic=O

        # Compute probability mass on O-series states
        beliefs = result["beliefs"]
        o_mass = sum(
            beliefs[i] for i in range(48)
            if index_to_state_v2(i)[3] == "O"
        )
        # O-series should have notable probability mass
        assert o_mass > 0.1, f"O-series mass: {o_mass}"

    def test_two_step_learning(self):
        """Running step twice changes beliefs (not identical output)."""
        from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2

        agent = HegemonikónFEPAgentV2()

        r1 = agent.step(observation=8)
        agent.update_A_dirichlet(observation=8)

        r2 = agent.step(observation=8)
        agent.update_A_dirichlet(observation=8)

        # Beliefs should differ between cycles
        # (Dirichlet update changes A matrix)
        diff = np.abs(r1["beliefs"] - r2["beliefs"]).sum()
        assert diff > 0.001, f"Beliefs unchanged after learning: diff={diff}"

    def test_persistence_v2(self):
        """Save and load A matrix for v2 agent."""
        from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2

        with tempfile.NamedTemporaryFile(suffix="_v2_A.npy", delete=False) as f:
            a_path = f.name
        Path(a_path).unlink(missing_ok=True)

        try:
            agent1 = HegemonikónFEPAgentV2()
            agent1.step(observation=8)
            agent1.update_A_dirichlet(observation=8)
            agent1.save_learned_A(a_path)

            agent2 = HegemonikónFEPAgentV2()
            loaded = agent2.load_learned_A(a_path)
            assert loaded is True

            # Check A matrices match
            A1 = agent1._get_A_matrix()
            A2 = agent2._get_A_matrix()
            np.testing.assert_allclose(A1, A2, atol=1e-10)
        finally:
            Path(a_path).unlink(missing_ok=True)
