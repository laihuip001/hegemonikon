# PROOF: [L3/テスト] 対象モジュールが存在→検証が必要
"""
Tests for FEP config module.
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from mekhane.fep.config import (
    FEPParameters,
    load_parameters,
    get_default_params,
    reload_params,
    AMatrixParams,
    BMatrixParams,
    CVectorParams,
    DVectorParams,
    HyperParams,
    PARAMETERS_PATH,
)


class TestFEPParameters:
    """Test FEPParameters dataclass."""

    def test_default_values(self):
        """Default values match literature."""
        params = FEPParameters()

        # A matrix (pymdp Tutorial 2 range: 0.7-0.9)
        assert params.A.high_reliability == 0.85
        assert params.A.low_reliability == 0.15

        # B matrix
        assert params.B.deterministic == 1.0
        assert params.B.observe_clarifies == 0.8

        # C vector (Gijsen et al. 2022)
        assert params.C.high_positive == 2.5
        assert params.C.high_negative == -2.0

        # D vector (pymdp default)
        assert params.D.uniform == 0.5

        # Hyperparams (pymdp Agent defaults)
        assert params.hyperparams.gamma == 16.0
        assert params.hyperparams.alpha == 16.0


class TestLoadParameters:
    """Test load_parameters function."""

    def test_load_from_default_path(self):
        """Load parameters from module directory."""
        if PARAMETERS_PATH.exists():
            params = load_parameters()
            assert params.version != "default"
            assert params.confidence != "default"

    def test_fallback_on_missing_file(self):
        """Fallback to defaults when file missing."""
        fake_path = Path("/nonexistent/parameters.yaml")
        params = load_parameters(fake_path)

        assert params.version == "default"
        assert params.A.high_reliability == 0.85

    def test_load_from_custom_yaml(self):
        """Load from custom YAML file."""
        custom_yaml = {
            "version": "test-1.0",
            "confidence": "test",
            "A_matrix": {
                "high_reliability": {"value": 0.9},
                "low_reliability": {"value": 0.1},
            },
            "hyperparameters": {
                "gamma": {"value": 32.0},
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(custom_yaml, f)
            temp_path = Path(f.name)

        try:
            params = load_parameters(temp_path)
            assert params.version == "test-1.0"
            assert params.A.high_reliability == 0.9
            assert params.hyperparams.gamma == 32.0
        finally:
            temp_path.unlink()


class TestParametersCaching:
    """Test parameter caching behavior."""

    def test_get_default_params_caching(self):
        """get_default_params returns cached singleton."""
        params1 = get_default_params()
        params2 = get_default_params()
        assert params1 is params2

    def test_reload_params(self):
        """reload_params forces fresh load."""
        params1 = get_default_params()
        params2 = reload_params()
        # New object but same values
        assert params2.A.high_reliability == params1.A.high_reliability


class TestIntegrationWithParametersYAML:
    """Integration tests with actual parameters.yaml."""

    def test_actual_yaml_structure(self):
        """Verify parameters.yaml has expected structure."""
        if not PARAMETERS_PATH.exists():
            pytest.skip("parameters.yaml not found")

        with open(PARAMETERS_PATH, "r") as f:
            data = yaml.safe_load(f)

        assert "version" in data
        assert "A_matrix" in data
        assert "B_matrix" in data
        assert "C_vector" in data
        assert "D_vector" in data
        assert "hyperparameters" in data

    def test_crossvalidated_values(self):
        """Verify parameters match cross-validated sources."""
        if not PARAMETERS_PATH.exists():
            pytest.skip("parameters.yaml not found")

        params = load_parameters()

        # pymdp Tutorial 2: 0.7-0.9 range
        assert 0.7 <= params.A.high_reliability <= 0.9

        # Da Costa et al. 2020: Dirichlet α=1.0
        assert params.A.dirichlet_alpha == 1.0

        # pymdp Agent default
        assert params.hyperparams.gamma == 16.0
