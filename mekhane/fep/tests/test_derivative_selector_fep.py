
import pytest
import json
import shutil
from pathlib import Path
from mekhane.fep.derivative_selector import (
    DerivativeFEPLearner,
    select_derivative,
    update_derivative_selector,
    _FEP_LEARNER
)

@pytest.fixture
def temp_learner_path(tmp_path):
    return tmp_path / "learned_derivatives.json"

def test_learner_initialization(temp_learner_path):
    learner = DerivativeFEPLearner(path=temp_learner_path)
    assert learner.matrices == {}
    assert learner.path == temp_learner_path

def test_learning_cycle(temp_learner_path):
    learner = DerivativeFEPLearner(path=temp_learner_path)

    theorem = "O1"
    derivative = "nous"
    context = "本質的な問題" # Encodes to something high in abstraction

    # 1. Infer before learning (should be None or empty)
    probs = learner.infer(theorem, context)
    assert probs is None

    # 2. Learn
    learner.learn(theorem, derivative, context, success=True)

    # 3. Infer after learning
    probs = learner.infer(theorem, context)
    assert probs is not None
    assert probs[derivative] > 0.33  # Should be dominant (1.0 vs 0.0 vs 0.0 initially, wait, I used uniform prior [1,1,1] so it becomes [2,1,1] -> 0.5)

    # With [1,1,1] prior, adding 1 to 'nous' (index 0) makes it [2,1,1]. Total 4.
    # P(nous) = 2/4 = 0.5
    assert abs(probs["nous"] - 0.5) < 0.01
    assert abs(probs["phro"] - 0.25) < 0.01
    assert abs(probs["meta"] - 0.25) < 0.01

def test_persistence(temp_learner_path):
    learner = DerivativeFEPLearner(path=temp_learner_path)
    learner.learn("O1", "nous", "test", success=True)

    # Verify file exists
    assert temp_learner_path.exists()

    # Load new learner from same path
    learner2 = DerivativeFEPLearner(path=temp_learner_path)
    assert learner2.matrices == learner.matrices

    # Verify content
    probs = learner2.infer("O1", "test")
    assert probs["nous"] == 0.5

def test_integration_select_derivative(monkeypatch, temp_learner_path):
    # Patch the global _FEP_LEARNER to use our temp path
    learner = DerivativeFEPLearner(path=temp_learner_path)
    # Train it to prefer 'meta' for a specific context
    context = "疑わしい" # reflection high
    learner.learn("O1", "meta", context, success=True)
    learner.learn("O1", "meta", context, success=True)
    # [1, 1, 3] -> 0.2, 0.2, 0.6

    # Monkeypatch the global instance in the module
    import mekhane.fep.derivative_selector
    monkeypatch.setattr(mekhane.fep.derivative_selector, "_FEP_LEARNER", learner)

    # Run select_derivative with use_fep=True
    # "疑わしい" usually triggers 'meta' anyway via keywords, but let's check rationale
    result = select_derivative("O1", context, use_fep=True)

    assert "FEP: meta" in result.rationale
    assert "(60%)" in result.rationale or "(0.60)" in result.rationale or "60%" in result.rationale

def test_update_derivative_selector_integration(monkeypatch, temp_learner_path):
    learner = DerivativeFEPLearner(path=temp_learner_path)
    import mekhane.fep.derivative_selector
    monkeypatch.setattr(mekhane.fep.derivative_selector, "_FEP_LEARNER", learner)

    update_derivative_selector("O2", "voli", "some context", success=True)

    probs = learner.infer("O2", "some context")
    assert probs["voli"] == 0.5
