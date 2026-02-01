# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/fep/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 → FEP エージェントにはパラメータがある
   → パラメータの読み込みと管理が必要
   → config.py が担う

Q.E.D.

---

FEP Agent Configuration

Loads parameters from parameters.yaml with literature-backed defaults.

Cross-validated sources:
- pymdp Tutorial 2 (two-armed bandit)
- Gijsen et al. (2022) Scientific Reports
- Da Costa et al. (2020) Neuroscience & Biobehavioral Reviews
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
import yaml

# Default path to parameters.yaml
PARAMETERS_PATH = Path(__file__).parent / "parameters.yaml"


@dataclass
class AMatrixParams:
    """Observation likelihood parameters P(o|s)."""

    high_reliability: float = 0.85
    low_reliability: float = 0.15  # noqa: AI-ALL
    dirichlet_alpha: float = 1.0


@dataclass
class BMatrixParams:
    """State transition parameters P(s'|s,a)."""

    deterministic: float = 1.0
    probabilistic: float = 0.85
    observe_clarifies: float = 0.8
    observe_induces_epoche: float = 0.3


@dataclass
class CVectorParams:
    """Preference vector parameters."""

    high_positive: float = 2.5
    medium_positive: float = 1.5
    neutral: float = 0.0
    medium_negative: float = -1.0
    high_negative: float = -2.0


@dataclass
class DVectorParams:
    """Initial belief parameters."""

    uniform: float = 0.5
    uncertain_bias: float = 0.6
    certain_bias: float = 0.4


@dataclass
class HyperParams:
    """Agent hyperparameters."""

    gamma: float = 16.0
    alpha: float = 16.0
    beta: float = 2.0
    lr_pA: float = 1.0
    lr_pD: float = 0.5


@dataclass
class HegemonikónParams:
    """Hegemonikón-specific parameters."""

    epoche_entropy_threshold: float = 1.0


@dataclass
class FEPParameters:
    """Complete FEP parameter set.

    Loaded from parameters.yaml or defaults to literature-backed values.
    """

    A: AMatrixParams = field(default_factory=AMatrixParams)
    B: BMatrixParams = field(default_factory=BMatrixParams)
    C: CVectorParams = field(default_factory=CVectorParams)
    D: DVectorParams = field(default_factory=DVectorParams)
    hyperparams: HyperParams = field(default_factory=HyperParams)
    hegemonikon: HegemonikónParams = field(default_factory=HegemonikónParams)

    # Metadata
    version: str = "default"
    confidence: str = "default"


def _extract_value(data: Dict[str, Any], key: str, default: float) -> float:
    """Extract value from nested YAML structure."""
    if key in data:
        item = data[key]
        if isinstance(item, dict) and "value" in item:
            return float(item["value"])
        elif isinstance(item, (int, float)):
            return float(item)
    return default


def load_parameters(path: Optional[Path] = None) -> FEPParameters:
    """Load FEP parameters from YAML file.

    Args:
        path: Path to parameters.yaml. Defaults to module directory.

    Returns:
        FEPParameters dataclass with loaded values.
        Falls back to defaults if file not found or parse error.
    """
    params = FEPParameters()
    target_path = path or PARAMETERS_PATH

    if not target_path.exists():
        return params

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (yaml.YAMLError, OSError) as e:
        # Fallback to defaults on error
        import warnings

        warnings.warn(f"Failed to load {target_path}: {e}. Using defaults.")
        return params

    if not data:
        return params

    # Extract metadata
    params.version = data.get("version", "unknown")
    params.confidence = data.get("confidence", "unknown")

    # A matrix
    if "A_matrix" in data:
        a_data = data["A_matrix"]
        params.A = AMatrixParams(
            high_reliability=_extract_value(a_data, "high_reliability", 0.85),
            low_reliability=_extract_value(a_data, "low_reliability", 0.15),
            dirichlet_alpha=_extract_value(a_data, "dirichlet_alpha", 1.0),
        )

    # B matrix
    if "B_matrix" in data:
        b_data = data["B_matrix"]
        params.B = BMatrixParams(
            deterministic=_extract_value(b_data, "deterministic", 1.0),
            probabilistic=_extract_value(b_data, "probabilistic", 0.85),
            observe_clarifies=_extract_value(b_data, "observe_clarifies", 0.8),
            observe_induces_epoche=_extract_value(
                b_data, "observe_induces_epochē", 0.3
            ),
        )

    # C vector
    if "C_vector" in data:
        c_data = data["C_vector"]
        params.C = CVectorParams(
            high_positive=_extract_value(c_data, "high_positive", 2.5),
            medium_positive=_extract_value(c_data, "medium_positive", 1.5),
            neutral=_extract_value(c_data, "neutral", 0.0),
            medium_negative=_extract_value(c_data, "medium_negative", -1.0),
            high_negative=_extract_value(c_data, "high_negative", -2.0),
        )

    # D vector
    if "D_vector" in data:
        d_data = data["D_vector"]
        params.D = DVectorParams(
            uniform=_extract_value(d_data, "uniform", 0.5),
            uncertain_bias=_extract_value(d_data, "uncertain_bias", 0.6),
            certain_bias=_extract_value(d_data, "certain_bias", 0.4),
        )

    # Hyperparameters
    if "hyperparameters" in data:
        h_data = data["hyperparameters"]
        params.hyperparams = HyperParams(
            gamma=_extract_value(h_data, "gamma", 16.0),
            alpha=_extract_value(h_data, "alpha", 16.0),
            beta=_extract_value(h_data, "beta", 2.0),
            lr_pA=_extract_value(h_data, "lr_pA", 1.0),
            lr_pD=_extract_value(h_data, "lr_pD", 0.5),
        )

    # Hegemonikón-specific
    if "hegemonikon" in data:
        hk_data = data["hegemonikon"]
        if "epochē_threshold" in hk_data:
            threshold_data = hk_data["epochē_threshold"]
            params.hegemonikon = HegemonikónParams(
                epoche_entropy_threshold=_extract_value(threshold_data, "entropy", 1.0),
            )

    return params


# Default parameters singleton (lazy loaded)
_default_params: Optional[FEPParameters] = None


def get_default_params() -> FEPParameters:
    """Get cached default parameters."""
    global _default_params
    if _default_params is None:
        _default_params = load_parameters()
    return _default_params


def reload_params() -> FEPParameters:
    """Force reload parameters from disk."""
    global _default_params
    _default_params = load_parameters()
    return _default_params
