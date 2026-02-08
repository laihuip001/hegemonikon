# PROOF: [L2/インフラ] <- mekhane/fep/
# PURPOSE: 48-state FEP Model (v2) — Series 統合状態空間
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 → FEP Agent は Series を知るべき
   → Series を hidden state factor に組み込む
   → state_spaces_v2.py が 48-state model を定義する

Q.E.D.

---

State Spaces v2 for Hegemonikón Active Inference

Extends v1 by adding Series (O/S/H/P/K/A) as a 4th hidden state factor
and series-specific actions, enabling unified cognitive-content judgment.

v1: phantasia(2) × assent(2) × horme(2) = 8 states, 2 actions
v2: phantasia(2) × assent(2) × horme(2) × series(6) = 48 states, 7 actions
"""

from typing import Dict, List, Tuple

# Re-export v1 factors for compatibility
from .state_spaces import (
    PHANTASIA_STATES,
    ASSENT_STATES,
    HORME_STATES,
    OBSERVATION_MODALITIES as V1_OBSERVATION_MODALITIES,
    PREFERENCES as V1_PREFERENCES,
)

# =============================================================================
# 4th Hidden State Factor: Series
# =============================================================================

SERIES_STATES: List[str] = ["O", "S", "H", "P", "K", "A"]

SERIES_NAMES: Dict[str, str] = {
    "O": "Ousia (本質)",
    "S": "Skhēma (設計)",
    "H": "Hormē (動機)",
    "P": "Perigraphē (環境)",
    "K": "Kairos (文脈)",
    "A": "Akribeia (精度)",
}

# =============================================================================
# Expanded Observation Modalities
# =============================================================================

OBSERVATION_MODALITIES_V2: Dict[str, List[str]] = {
    # v1 modalities (unchanged)
    "context": ["ambiguous", "clear"],
    "urgency": ["low", "medium", "high"],
    "confidence": ["low", "medium", "high"],
    # NEW: Topic modality from Attractor
    "topic": ["O", "S", "H", "P", "K", "A"],
}

# =============================================================================
# Expanded Actions
# =============================================================================

ACTIONS_V2: List[str] = [
    "observe",   # 0: Epochē — 判断停止、観察モード
    "act_O",     # 1: O-series WF 実行 (Ousia/本質)
    "act_S",     # 2: S-series WF 実行 (Skhēma/設計)
    "act_H",     # 3: H-series WF 実行 (Hormē/動機)
    "act_P",     # 4: P-series WF 実行 (Perigraphē/環境)
    "act_K",     # 5: K-series WF 実行 (Kairos/文脈)
    "act_A",     # 6: A-series WF 実行 (Akribeia/精度)
]

# Action → Series mapping
ACTION_TO_SERIES: Dict[str, str] = {
    "act_O": "O", "act_S": "S", "act_H": "H",
    "act_P": "P", "act_K": "K", "act_A": "A",
}

# =============================================================================
# Preference Vectors (C matrix)
# =============================================================================

PREFERENCES_V2: Dict[str, Dict[str, float]] = {
    **V1_PREFERENCES,
    "topic": {
        # 全 Series は等価に好ましい — 特定の Series への偏向なし
        "O": 0.5, "S": 0.5, "H": 0.5,
        "P": 0.5, "K": 0.5, "A": 0.5,
    },
}

# =============================================================================
# Dimensions
# =============================================================================

NUM_STATES_V2 = (
    len(PHANTASIA_STATES)
    * len(ASSENT_STATES)
    * len(HORME_STATES)
    * len(SERIES_STATES)
)  # 2 × 2 × 2 × 6 = 48

NUM_OBS_V2 = sum(len(v) for v in OBSERVATION_MODALITIES_V2.values())  # 14

NUM_ACTIONS_V2 = len(ACTIONS_V2)  # 7


# =============================================================================
# Helper Functions
# =============================================================================


def get_state_dim_v2() -> int:
    """Return total hidden state dimension for v2 model."""
    return NUM_STATES_V2


def get_obs_dim_v2() -> Dict[str, int]:
    """Return observation dimensions for v2 model."""
    return {k: len(v) for k, v in OBSERVATION_MODALITIES_V2.items()}


def state_to_index_v2(
    phantasia: str, assent: str, horme: str, series: str
) -> int:
    """Convert 4-factor state to flat index.

    Order: phantasia × assent × horme × series (row-major)
    """
    p_idx = PHANTASIA_STATES.index(phantasia)
    a_idx = ASSENT_STATES.index(assent)
    h_idx = HORME_STATES.index(horme)
    s_idx = SERIES_STATES.index(series)

    a_size = len(ASSENT_STATES)
    h_size = len(HORME_STATES)
    s_size = len(SERIES_STATES)

    return (
        p_idx * a_size * h_size * s_size
        + a_idx * h_size * s_size
        + h_idx * s_size
        + s_idx
    )


def index_to_state_v2(idx: int) -> Tuple[str, str, str, str]:
    """Convert flat index to 4-factor state names.

    Returns:
        (phantasia, assent, horme, series)
    """
    s_size = len(SERIES_STATES)
    h_size = len(HORME_STATES)
    a_size = len(ASSENT_STATES)

    s_idx = idx % s_size
    h_idx = (idx // s_size) % h_size
    a_idx = (idx // (s_size * h_size)) % a_size
    p_idx = idx // (s_size * h_size * a_size)

    return (
        PHANTASIA_STATES[p_idx],
        ASSENT_STATES[a_idx],
        HORME_STATES[h_idx],
        SERIES_STATES[s_idx],
    )


def action_name_v2(action_idx: int) -> str:
    """Convert action index to human-readable name."""
    if 0 <= action_idx < len(ACTIONS_V2):
        return ACTIONS_V2[action_idx]
    return f"unknown_{action_idx}"


def action_to_series(action_idx: int) -> str | None:
    """Get the Series associated with an action (None for observe)."""
    name = action_name_v2(action_idx)
    return ACTION_TO_SERIES.get(name)
