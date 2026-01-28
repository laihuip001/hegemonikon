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
from .fep_bridge import (
    noesis_analyze,
    boulesis_analyze,
    full_inference_cycle,
    NoesisResult,
    BoulesisResult,
)
from .llm_evaluator import (
    encode_input_with_confidence,
    hierarchical_evaluate,
    evaluate_and_infer,
    EvaluationResult,
    GEMINI_AVAILABLE,
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
    "noesis_analyze",
    "boulesis_analyze",
    "full_inference_cycle",
    "NoesisResult",
    "BoulesisResult",
    "encode_input_with_confidence",
    "hierarchical_evaluate",
    "evaluate_and_infer",
    "EvaluationResult",
    "GEMINI_AVAILABLE",
]

