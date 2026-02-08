# PROOF: [L2/テスト] <- mekhane/fep/tests/
"""Tests for Precision Weighting in HegemonikónFEPAgent.

Verifies that:
- Initial precision weights are uniform (1.0 for all modalities)
- Accurate predictions increase precision
- Inaccurate predictions decrease precision
- Precision scaling correctly modifies the A matrix
- step() integrates precision weighting automatically
- _decompose_observation correctly inverts encode_observation
"""

import pytest
import numpy as np

from mekhane.fep.fep_agent import HegemonikónFEPAgent
from mekhane.fep.state_spaces import OBSERVATION_MODALITIES


class TestPrecisionWeighting:
    """Precision Weighting のテスト"""

    @pytest.fixture
    def agent(self):
        return HegemonikónFEPAgent(use_defaults=True)

    def test_initial_precision_uniform(self, agent: HegemonikónFEPAgent):
        """初期精度は全 modality で 1.0"""
        for modality, weight in agent.precision_weights.items():
            assert weight == 1.0, f"{modality} should start at 1.0"

    def test_accurate_prediction_increases_precision(self, agent: HegemonikónFEPAgent):
        """正確な予測後、精度が維持される (1.0 に近い)"""
        # Same observation = perfect accuracy
        agent.update_precision(observed=5, predicted=5)
        for modality, weight in agent.precision_weights.items():
            assert weight >= 0.99, f"{modality} should stay near 1.0 after match"

    def test_inaccurate_prediction_decreases_precision(self, agent: HegemonikónFEPAgent):
        """不正確な予測後、精度が下がる"""
        # Very different observations
        agent.update_precision(observed=0, predicted=7)
        # At least one modality should have decreased
        any_decreased = any(w < 1.0 for w in agent.precision_weights.values())
        assert any_decreased, "At least one modality should decrease on mismatch"

    def test_repeated_errors_converge_lower(self, agent: HegemonikónFEPAgent):
        """繰り返しの予測誤差で精度が収束的に低下する"""
        initial = dict(agent.precision_weights)
        for _ in range(10):
            agent.update_precision(observed=0, predicted=7)
        for modality in agent.precision_weights:
            assert agent.precision_weights[modality] < initial[modality], (
                f"{modality} should be lower after repeated errors"
            )

    def test_apply_precision_modifies_A(self, agent: HegemonikónFEPAgent):
        """_apply_precision がA行列を変更する"""
        # Cache base A
        agent._apply_precision()
        base_A = agent._base_A.copy()

        # Lower precision for context
        agent.precision_weights["context"] = 0.3
        agent._apply_precision()

        # Get current A
        A = agent.agent.A
        if isinstance(A, np.ndarray) and A.dtype == object:
            current_A = np.asarray(A[0], dtype=np.float64)
        elif isinstance(A, list):
            current_A = np.asarray(A[0], dtype=np.float64)
        else:
            current_A = np.asarray(A, dtype=np.float64)

        # Context rows (0-1) should differ from base
        context_dim = len(OBSERVATION_MODALITIES["context"])
        context_diff = np.abs(current_A[:context_dim] - base_A[:context_dim]).sum()
        assert context_diff > 0.01, "Context rows should change with low precision"

    def test_apply_precision_preserves_normalization(self, agent: HegemonikónFEPAgent):
        """precision scaling 後もA行列の列が正規化されている"""
        agent.precision_weights["urgency"] = 0.5
        agent._apply_precision()

        A = agent.agent.A
        if isinstance(A, np.ndarray) and A.dtype == object:
            A_matrix = np.asarray(A[0], dtype=np.float64)
        elif isinstance(A, list):
            A_matrix = np.asarray(A[0], dtype=np.float64)
        else:
            A_matrix = np.asarray(A, dtype=np.float64)

        col_sums = A_matrix.sum(axis=0)
        np.testing.assert_allclose(col_sums, 1.0, atol=1e-10,
                                   err_msg="Columns should sum to 1.0")

    def test_step_includes_precision_weights(self, agent: HegemonikónFEPAgent):
        """step() が precision_weights を返す"""
        result = agent.step(observation=3)
        assert "precision_weights" in result, "step should return precision_weights"
        assert isinstance(result["precision_weights"], dict)
        assert set(result["precision_weights"].keys()) == {"context", "urgency", "confidence"}

    def test_step_records_precision_in_history(self, agent: HegemonikónFEPAgent):
        """step() が precision_update を history に記録する"""
        agent.step(observation=3)
        precision_updates = [h for h in agent.get_history() if h["type"] == "precision_update"]
        assert len(precision_updates) >= 1, "step should record precision_update"

    def test_decompose_observation_context(self):
        """_decompose_observation: high flat_idx → context=clear"""
        result = HegemonikónFEPAgent._decompose_observation(5)
        assert result["context"] == 1, "flat_idx >= 4 should be clear context"

    def test_decompose_observation_low(self):
        """_decompose_observation: low flat_idx → context=ambiguous"""
        result = HegemonikónFEPAgent._decompose_observation(1)
        assert result["context"] == 0, "flat_idx < 4 should be ambiguous context"

    def test_get_predicted_observation(self, agent: HegemonikónFEPAgent):
        """_get_predicted_observation が valid な確率分布を返す"""
        pred = agent._get_predicted_observation()
        assert isinstance(pred, np.ndarray)
        assert pred.shape[0] == sum(len(v) for v in OBSERVATION_MODALITIES.values())
        # Should sum to approximately 1 (probability distribution)
        np.testing.assert_allclose(pred.sum(), 1.0, atol=0.01,
                                   err_msg="Predicted observation should be ~probability dist")
