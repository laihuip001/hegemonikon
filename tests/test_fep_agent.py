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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
