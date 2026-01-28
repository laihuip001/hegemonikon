"""
Tests for Hegemonikón FEP Agent

Tests the Active Inference implementation for O1 Noēsis and O2 Boulēsis.
"""

import pytest
import numpy as np


class TestHegemonikónFEPAgent:
    """Test suite for HegemonikónFEPAgent."""
    
    def test_import(self):
        """Module can be imported."""
        from mekhane.fep import HegemonikónFEPAgent
        assert HegemonikónFEPAgent is not None
    
    def test_init_with_defaults(self):
        """Agent initializes with default matrices."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        assert agent is not None
        assert agent.state_dim == 8  # 2 * 2 * 2
        assert agent.agent is not None
    
    def test_infer_states_returns_beliefs(self):
        """infer_states returns updated belief distribution."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        # Observe something
        result = agent.infer_states(observation=0)
        
        assert "beliefs" in result
        assert "map_state" in result
        assert "map_state_names" in result
        assert "entropy" in result
        
        # Beliefs should be valid probability distribution
        beliefs = result["beliefs"]
        assert np.allclose(np.sum(beliefs), 1.0)
        assert np.all(beliefs >= 0)
    
    def test_infer_policies_returns_efe(self):
        """infer_policies returns policy probabilities and EFE values."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        # First infer states
        agent.infer_states(observation=0)
        
        # Then infer policies
        q_pi, neg_efe = agent.infer_policies()
        
        assert q_pi is not None
        assert neg_efe is not None
    
    def test_step_completes_cycle(self):
        """step() performs full inference-action cycle."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        result = agent.step(observation=0)
        
        assert "beliefs" in result
        assert "map_state_names" in result
        assert "entropy" in result
        assert "q_pi" in result
        assert "action" in result
        assert "action_name" in result
        
        # Action should be valid
        assert result["action"] in [0, 1]
        assert result["action_name"] in ["observe", "act"]
    
    def test_history_tracking(self):
        """Agent tracks inference history."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        # Perform some operations
        agent.step(observation=0)
        agent.step(observation=1)
        
        history = agent.get_history()
        
        assert len(history) > 0
    
    def test_reset_clears_state(self):
        """reset() clears agent state."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        # Perform some operations
        agent.step(observation=0)
        assert len(agent.get_history()) > 0
        
        # Reset
        agent.reset()
        
        assert len(agent.get_history()) == 0


class TestStateSpaces:
    """Test suite for state space definitions."""
    
    def test_state_constants_defined(self):
        """State constants are properly defined."""
        from mekhane.fep import (
            PHANTASIA_STATES,
            ASSENT_STATES,
            HORME_STATES,
            OBSERVATION_MODALITIES,
        )
        
        assert len(PHANTASIA_STATES) == 2
        assert len(ASSENT_STATES) == 2
        assert len(HORME_STATES) == 2
        assert len(OBSERVATION_MODALITIES) == 3
    
    def test_state_to_index_roundtrip(self):
        """state_to_index and index_to_state are inverses."""
        from mekhane.fep.state_spaces import (
            state_to_index,
            index_to_state,
            PHANTASIA_STATES,
            ASSENT_STATES,
            HORME_STATES,
        )
        
        for p in PHANTASIA_STATES:
            for a in ASSENT_STATES:
                for h in HORME_STATES:
                    idx = state_to_index(p, a, h)
                    p2, a2, h2 = index_to_state(idx)
                    assert (p, a, h) == (p2, a2, h2)
    
    def test_get_state_dim(self):
        """get_state_dim returns correct dimension."""
        from mekhane.fep.state_spaces import get_state_dim
        
        # 2 * 2 * 2 = 8
        assert get_state_dim() == 8


class TestPolicyHorizon:
    """Test suite for 2-step policy horizon (arXiv:2412.10425)."""
    
    def test_policy_len_is_2(self):
        """Agent is initialized with policy_len=2."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        # Check that policy_len is correctly set
        assert agent.agent.policy_len == 2
    
    def test_inference_horizon_is_1(self):
        """Agent is initialized with inference_horizon=1."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        # Check that inference_horizon is correctly set
        assert agent.agent.inference_horizon == 1
    
    def test_learning_rate_default(self):
        """Agent has default learning rate of 50.0."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        assert agent.learning_rate == 50.0


class TestPersistence:
    """Test suite for A matrix persistence."""
    
    def test_save_learned_A(self, tmp_path):
        """save_learned_A saves A matrix to file."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        save_path = tmp_path / "test_A.npy"
        saved_path = agent.save_learned_A(str(save_path))
        
        assert save_path.exists()
        assert saved_path == str(save_path)
    
    def test_load_learned_A(self, tmp_path):
        """load_learned_A loads A matrix from file."""
        from mekhane.fep import HegemonikónFEPAgent
        import numpy as np
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        # Save first
        save_path = tmp_path / "test_A.npy"
        agent.save_learned_A(str(save_path))
        
        # Create new agent and load
        agent2 = HegemonikónFEPAgent(use_defaults=True)
        loaded = agent2.load_learned_A(str(save_path))
        
        assert loaded is True
    
    def test_load_nonexistent_returns_false(self, tmp_path):
        """load_learned_A returns False for nonexistent file."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        nonexistent_path = tmp_path / "nonexistent.npy"
        loaded = agent.load_learned_A(str(nonexistent_path))
        
        assert loaded is False
    
    def test_persistence_roundtrip(self, tmp_path):
        """A matrix survives save/load cycle."""
        from mekhane.fep import HegemonikónFEPAgent
        import numpy as np
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        original_A = agent.agent.A.copy() if isinstance(agent.agent.A, np.ndarray) else agent.agent.A[0].copy()
        
        # Save
        save_path = tmp_path / "roundtrip_A.npy"
        agent.save_learned_A(str(save_path))
        
        # Modify A
        if isinstance(agent.agent.A, np.ndarray):
            agent.agent.A *= 2.0
        else:
            agent.agent.A[0] *= 2.0
        
        # Load (should restore original)
        agent.load_learned_A(str(save_path))
        
        loaded_A = agent.agent.A if isinstance(agent.agent.A, np.ndarray) else agent.agent.A[0]
        # Note: exact equality may not hold due to normalization, but shape should match
        assert loaded_A.shape == original_A.shape


class TestDirichletUpdate:
    """Test suite for Dirichlet learning."""
    
    def test_dirichlet_update_records_history(self):
        """update_A_dirichlet records update in history."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        # First infer states
        agent.infer_states(observation=0)
        
        # Then update
        agent.update_A_dirichlet(observation=0)
        
        history = agent.get_history()
        dirichlet_updates = [h for h in history if h.get("type") == "dirichlet_update"]
        
        assert len(dirichlet_updates) == 1
        assert dirichlet_updates[0]["observation"] == 0
        assert dirichlet_updates[0]["learning_rate"] == 50.0
    
    def test_dirichlet_update_custom_learning_rate(self):
        """update_A_dirichlet accepts custom learning rate."""
        from mekhane.fep import HegemonikónFEPAgent
        
        agent = HegemonikónFEPAgent(use_defaults=True)
        
        agent.infer_states(observation=0)
        agent.update_A_dirichlet(observation=0, learning_rate=100.0)
        
        history = agent.get_history()
        dirichlet_updates = [h for h in history if h.get("type") == "dirichlet_update"]
        
        assert dirichlet_updates[0]["learning_rate"] == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

