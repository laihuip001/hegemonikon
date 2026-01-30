# PROOF: [L3/テスト] 対象モジュールが存在→検証が必要
"""Tests for LLM Evaluator - Hierarchical Hybrid Evaluation."""

import pytest


class TestEncodeInputWithConfidence:
    """Tests for L1 encode_input_with_confidence."""
    
    def test_returns_tuple_and_confidence(self):
        """Returns observation tuple and confidence score."""
        from mekhane.fep.llm_evaluator import encode_input_with_confidence
        
        obs, confidence = encode_input_with_confidence("test input")
        
        assert isinstance(obs, tuple)
        assert len(obs) == 3
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
    
    def test_high_confidence_for_detailed_input(self):
        """Detailed input should have higher confidence."""
        from mekhane.fep.llm_evaluator import encode_input_with_confidence
        
        # Short input
        _, short_conf = encode_input_with_confidence("ok")
        
        # Detailed input with patterns
        _, long_conf = encode_input_with_confidence(
            "緊急: ファイル path/to/file.py のコードを修正してください。"
            "具体的には関数 foo() のバグを修正する必要があります。"
        )
        
        assert long_conf > short_conf
    
    def test_simple_y_approval(self):
        """Simple 'y' should be parsed correctly."""
        from mekhane.fep.llm_evaluator import encode_input_with_confidence
        
        obs, confidence = encode_input_with_confidence("y")
        
        # 'y' = high confidence input
        assert obs[2] == 2  # high confidence index


class TestHierarchicalEvaluate:
    """Tests for hierarchical_evaluate."""
    
    def test_returns_evaluation_result(self):
        """Returns an EvaluationResult dataclass."""
        from mekhane.fep.llm_evaluator import hierarchical_evaluate, EvaluationResult
        
        result = hierarchical_evaluate("test input")
        
        assert isinstance(result, EvaluationResult)
    
    def test_uses_l1_for_simple_cases(self):
        """Uses L1 for simple, clear cases."""
        from mekhane.fep.llm_evaluator import hierarchical_evaluate
        
        # Force L1
        result = hierarchical_evaluate("y", force_layer="L1")
        
        assert result.layer_used == "L1"
    
    def test_observation_is_valid_tuple(self):
        """Observation should be valid tuple of indices."""
        from mekhane.fep.llm_evaluator import hierarchical_evaluate
        
        result = hierarchical_evaluate("test")
        
        assert len(result.observation) == 3
        assert result.observation[0] in (0, 1)  # context
        assert result.observation[1] in (0, 1, 2)  # urgency
        assert result.observation[2] in (0, 1, 2)  # confidence
    
    def test_confidence_in_valid_range(self):
        """Confidence should be between 0 and 1."""
        from mekhane.fep.llm_evaluator import hierarchical_evaluate
        
        result = hierarchical_evaluate("test input text")
        
        assert 0 <= result.confidence <= 1
    
    def test_interpretation_is_populated(self):
        """Interpretation should be a non-empty string."""
        from mekhane.fep.llm_evaluator import hierarchical_evaluate
        
        result = hierarchical_evaluate("test")
        
        assert isinstance(result.interpretation, str)
        assert len(result.interpretation) > 0


class TestScoresToObservation:
    """Tests for scores_to_observation."""
    
    def test_converts_scores_correctly(self):
        """Converts LLM scores to observation indices."""
        from mekhane.fep.llm_evaluator import scores_to_observation
        
        scores = {
            "context_clarity": 0.8,  # clear (1)
            "urgency": 0.7,  # high (2)
            "confidence": 0.5,  # medium (1)
        }
        
        obs = scores_to_observation(scores)
        
        assert obs == (1, 2, 1)
    
    def test_handles_boundary_cases(self):
        """Handles boundary values correctly."""
        from mekhane.fep.llm_evaluator import scores_to_observation
        
        # All zeros
        obs_low = scores_to_observation({
            "context_clarity": 0.0,
            "urgency": 0.0,
            "confidence": 0.0,
        })
        assert obs_low == (0, 0, 0)
        
        # All ones
        obs_high = scores_to_observation({
            "context_clarity": 1.0,
            "urgency": 1.0,
            "confidence": 1.0,
        })
        assert obs_high == (1, 2, 2)


class TestEvaluateAndInfer:
    """Tests for evaluate_and_infer integration."""
    
    def test_returns_combined_result(self):
        """Returns dict with evaluation, fep, and combined_feedback."""
        from mekhane.fep.llm_evaluator import evaluate_and_infer
        
        result = evaluate_and_infer("test input")
        
        assert "evaluation" in result
        assert "fep" in result
        assert "combined_feedback" in result
    
    def test_evaluation_section_has_required_keys(self):
        """Evaluation section has observation, confidence, layer."""
        from mekhane.fep.llm_evaluator import evaluate_and_infer
        
        result = evaluate_and_infer("test")
        
        assert "observation" in result["evaluation"]
        assert "confidence" in result["evaluation"]
        assert "layer" in result["evaluation"]
    
    def test_fep_section_has_action(self):
        """FEP section includes action recommendation."""
        from mekhane.fep.llm_evaluator import evaluate_and_infer
        
        result = evaluate_and_infer("test")
        
        assert "action_name" in result["fep"]
        assert result["fep"]["action_name"] in ["observe", "act"]
    
    def test_combined_feedback_is_string(self):
        """Combined feedback is a formatted string."""
        from mekhane.fep.llm_evaluator import evaluate_and_infer
        
        result = evaluate_and_infer("test input")
        
        assert isinstance(result["combined_feedback"], str)
        assert "Hierarchical Evaluation" in result["combined_feedback"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
