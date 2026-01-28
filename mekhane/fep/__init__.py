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
from .encoding import (
    encode_input,
    encode_structured_input,
    decode_observation,
)
from .persistence import (
    save_A,
    load_A,
    A_exists,
    LEARNED_A_PATH,
)

__all__ = [
    "HegemonikónFEPAgent",
    "PHANTASIA_STATES",
    "ASSENT_STATES",
    "HORME_STATES",
    "OBSERVATION_MODALITIES",
    "encode_input",
    "encode_structured_input",
    "decode_observation",
    "save_A",
    "load_A",
    "A_exists",
    "LEARNED_A_PATH",
]
