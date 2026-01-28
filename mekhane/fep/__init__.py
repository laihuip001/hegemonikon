"""
Hegemonikón FEP Module

Active Inference implementation based on pymdp for cognitive processes.
"""

from .fep_agent import HegemonikónFEPAgent
from .state_spaces import (
    PHANTASIA_STATES,
    ASSENT_STATES,
    HORME_STATES,
    OBSERVATION_MODALITIES,
)

__all__ = [
    "HegemonikónFEPAgent",
    "PHANTASIA_STATES",
    "ASSENT_STATES",
    "HORME_STATES",
    "OBSERVATION_MODALITIES",
]
