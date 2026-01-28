"""
State Spaces for Hegemonikón Active Inference

Maps Stoic philosophy concepts to FEP state factors and observation modalities.

References:
- Stoic-FEP Correspondence (stoic_hegemonikon_comparison.md)
- Active Inference & FEP Technical Implementation KI
"""

from typing import List, Dict

# =============================================================================
# State Factors (Hidden States)
# =============================================================================

# O1 Noēsis: Phantasia (Impression) clarity
PHANTASIA_STATES: List[str] = [
    "uncertain",  # Impression is unclear, requires investigation
    "clear",      # Impression is clear, ready for assent
]

# Assent (Syncatasthesis): Belief commitment level
ASSENT_STATES: List[str] = [
    "withheld",   # Epochē - judgment suspended
    "granted",    # Assent given - belief committed
]

# O2 Boulēsis: Hormē (Impulse) for action
HORME_STATES: List[str] = [
    "passive",    # No action impulse
    "active",     # Action impulse present
]

# =============================================================================
# Observation Modalities
# =============================================================================

OBSERVATION_MODALITIES: Dict[str, List[str]] = {
    # Context clarity (from Anti-Skip Protocol)
    "context": ["ambiguous", "clear"],
    
    # Urgency level (from K-series Kairos)
    "urgency": ["low", "medium", "high"],
    
    # Confidence level (from A-series Akribeia)
    "confidence": ["low", "medium", "high"],
}

# =============================================================================
# Preference Vectors (C matrix)
# =============================================================================

# Preferred observations for each modality
PREFERENCES: Dict[str, Dict[str, float]] = {
    "context": {
        "ambiguous": -2.0,  # Avoid ambiguity (Zero Entropy principle)
        "clear": 2.0,
    },
    "urgency": {
        "low": 0.0,
        "medium": 0.5,
        "high": 1.0,       # Slightly prefer acting on urgent matters
    },
    "confidence": {
        "low": -1.0,       # Avoid low confidence (Epochē trigger)
        "medium": 0.5,
        "high": 1.5,
    },
}

# =============================================================================
# Helper Functions
# =============================================================================

def get_state_dim() -> int:
    """Return the total number of hidden state factors."""
    return len(PHANTASIA_STATES) * len(ASSENT_STATES) * len(HORME_STATES)


def get_obs_dim() -> Dict[str, int]:
    """Return the dimension of each observation modality."""
    return {k: len(v) for k, v in OBSERVATION_MODALITIES.items()}


def state_to_index(phantasia: str, assent: str, horme: str) -> int:
    """Convert state names to flat index.
    
    Args:
        phantasia: Phantasia state name
        assent: Assent state name
        horme: Hormē state name
        
    Returns:
        Flat index into state space
    """
    p_idx = PHANTASIA_STATES.index(phantasia)
    a_idx = ASSENT_STATES.index(assent)
    h_idx = HORME_STATES.index(horme)
    
    # Compute flat index (row-major order)
    return (p_idx * len(ASSENT_STATES) * len(HORME_STATES) +
            a_idx * len(HORME_STATES) +
            h_idx)


def index_to_state(idx: int) -> tuple:
    """Convert flat index back to state names.
    
    Args:
        idx: Flat index into state space
        
    Returns:
        Tuple of (phantasia, assent, horme) state names
    """
    h_size = len(HORME_STATES)
    a_size = len(ASSENT_STATES)
    
    h_idx = idx % h_size
    a_idx = (idx // h_size) % a_size
    p_idx = idx // (h_size * a_size)
    
    return (PHANTASIA_STATES[p_idx], ASSENT_STATES[a_idx], HORME_STATES[h_idx])
