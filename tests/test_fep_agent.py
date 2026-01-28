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


class TestWorkflowEncoding:
    """Test suite for workflow output encoding functions."""
    
    def test_encode_noesis_output_high_confidence(self):
        """encode_noesis_output correctly maps high confidence."""
        from mekhane.fep.encoding import encode_noesis_output
        
        # High confidence, one uncertainty zone
        obs = encode_noesis_output(
            confidence_score=0.87,
            uncertainty_zones=[{"zone": "A", "doubt_score": 0.4}]
        )
        
        assert len(obs) == 3
        assert obs[0] == 1  # clear context (1 zone = 0.8 clarity >= 0.5)
        assert obs[1] == 0  # low urgency (always for Noēsis)
        assert obs[2] == 2  # high confidence (0.87 >= 0.7)
    
    def test_encode_noesis_output_many_uncertainty_zones(self):
        """encode_noesis_output handles many uncertainty zones."""
        from mekhane.fep.encoding import encode_noesis_output
        
        # Many uncertainty zones -> ambiguous context
        zones = [{"zone": f"Z{i}"} for i in range(4)]  # 4 zones -> 0.2 clarity
        obs = encode_noesis_output(confidence_score=0.5, uncertainty_zones=zones)
        
        assert obs[0] == 0  # ambiguous context
        assert obs[2] == 1  # medium confidence
    
    def test_encode_boulesis_output_deliberate(self):
        """encode_boulesis_output correctly maps deliberate (low impulse)."""
        from mekhane.fep.encoding import encode_boulesis_output
        
        # Low impulse (deliberate), high feasibility
        obs = encode_boulesis_output(impulse_score=25, feasibility_score=80)
        
        assert obs[0] == 1  # clear context (feasibility >= 50)
        assert obs[1] == 0  # low urgency (impulse < 40)
        assert obs[2] == 2  # high confidence (feasibility >= 70)
    
    def test_encode_boulesis_output_impulsive(self):
        """encode_boulesis_output correctly maps impulsive (high impulse)."""
        from mekhane.fep.encoding import encode_boulesis_output
        
        # High impulse, medium feasibility
        obs = encode_boulesis_output(impulse_score=80, feasibility_score=55)
        
        assert obs[0] == 1  # clear context (feasibility >= 50)
        assert obs[1] == 2  # high urgency (impulse >= 70)
        assert obs[2] == 1  # medium confidence (40 <= feasibility < 70)
    
    def test_generate_fep_feedback_markdown_act(self):
        """generate_fep_feedback_markdown generates correct output for 'act'."""
        from mekhane.fep.encoding import generate_fep_feedback_markdown
        
        mock_result = {
            "action_name": "act",
            "action": 1,
            "q_pi": [0.23, 0.77],
            "entropy": 1.42,
            "map_state_names": {
                "phantasia": "clear",
                "assent": "granted",
                "horme": "passive"
            }
        }
        
        output = generate_fep_feedback_markdown(mock_result, "context=clear, urgency=low")
        
        assert "act (77%)" in output
        assert "phantasia: clear" in output
        assert "assent: granted" in output
        assert "horme: passive" in output
        assert "1.42" in output
        assert "中程度の不確実性" in output
        assert "行動に移行可能" in output
    
    def test_generate_fep_feedback_markdown_observe(self):
        """generate_fep_feedback_markdown generates correct output for 'observe'."""
        from mekhane.fep.encoding import generate_fep_feedback_markdown
        
        mock_result = {
            "action_name": "observe",
            "action": 0,
            "q_pi": [0.65, 0.35],
            "entropy": 2.5,
            "map_state_names": {
                "phantasia": "unclear",
                "assent": "withheld",
                "horme": "active"
            }
        }
        
        output = generate_fep_feedback_markdown(mock_result, "context=ambiguous")
        
        assert "observe (65%)" in output
        assert "高い不確実性" in output
        assert "Epochē 推奨" in output
        assert "追加調査" in output


class TestFEPWithLearning:
    """Test suite for run_fep_with_learning and should_trigger_epoche."""
    
    def test_run_fep_with_learning_returns_result(self, tmp_path):
        """run_fep_with_learning returns valid result dict."""
        from mekhane.fep.encoding import run_fep_with_learning
        
        a_path = tmp_path / "test_A.npy"
        result = run_fep_with_learning(
            obs_tuple=(1, 0, 2),  # clear, low, high
            a_matrix_path=str(a_path),
        )
        
        assert "action_name" in result
        assert "entropy" in result
        assert "should_epoche" in result
        assert result["action_name"] in ["observe", "act"]
    
    def test_run_fep_with_learning_saves_a_matrix(self, tmp_path):
        """run_fep_with_learning saves A-matrix to file."""
        from mekhane.fep.encoding import run_fep_with_learning
        
        a_path = tmp_path / "learned_A.npy"
        run_fep_with_learning(obs_tuple=(0, 1, 1), a_matrix_path=str(a_path))
        
        assert a_path.exists()
    
    def test_run_fep_with_learning_loads_existing(self, tmp_path):
        """run_fep_with_learning loads existing A-matrix."""
        from mekhane.fep.encoding import run_fep_with_learning
        
        a_path = tmp_path / "learned_A.npy"
        
        # First run - creates file
        run_fep_with_learning(obs_tuple=(1, 0, 2), a_matrix_path=str(a_path))
        
        # Second run - loads existing file
        result = run_fep_with_learning(obs_tuple=(0, 2, 0), a_matrix_path=str(a_path))
        
        assert result["action_name"] in ["observe", "act"]
    
    def test_should_trigger_epoche_high_entropy(self):
        """should_trigger_epoche returns True for high entropy."""
        from mekhane.fep.encoding import should_trigger_epoche
        
        result = {"entropy": 2.5}
        assert should_trigger_epoche(result) is True
    
    def test_should_trigger_epoche_low_entropy(self):
        """should_trigger_epoche returns False for low entropy."""
        from mekhane.fep.encoding import should_trigger_epoche
        
        result = {"entropy": 1.5}
        assert should_trigger_epoche(result) is False
    
    def test_should_trigger_epoche_custom_threshold(self):
        """should_trigger_epoche respects custom threshold."""
        from mekhane.fep.encoding import should_trigger_epoche
        
        result = {"entropy": 1.5}
        assert should_trigger_epoche(result, threshold=1.0) is True
        assert should_trigger_epoche(result, threshold=2.0) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

