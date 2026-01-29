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
    encode_noesis_output,
    encode_boulesis_output,
    generate_fep_feedback_markdown,
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
from .config import (
    FEPParameters,
    load_parameters,
    get_default_params,
    reload_params,
)
from .telos_checker import (
    AlignmentStatus,
    TelосResult,
    check_alignment,
    format_telos_markdown,
    encode_telos_observation,
)
from .tekhne_registry import (
    TechniqueQuadrant,
    ActionCategory,
    Technique,
    TekhnēRegistry,
    STANDARD_TECHNIQUES,
    get_registry,
    search_techniques,
    format_registry_markdown,
)
from .energeia_executor import (
    ExecutionPhase,
    ExecutionStatus,
    ExecutionContext,
    ExecutionResult,
    EnergеiaExecutor,
    format_execution_markdown,
    encode_execution_observation,
)
from .chronos_evaluator import (
    TimeScale,
    CertaintyLevel,
    SlackLevel,
    ChronosResult,
    evaluate_time,
    format_chronos_markdown,
    encode_chronos_observation,
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
    "encode_noesis_output",
    "encode_boulesis_output",
    "generate_fep_feedback_markdown",
    "FEPParameters",
    "load_parameters",
    "get_default_params",
    "reload_params",
    # K3 Telos
    "AlignmentStatus",
    "TelосResult",
    "check_alignment",
    "format_telos_markdown",
    "encode_telos_observation",
    # P4 Tekhnē
    "TechniqueQuadrant",
    "ActionCategory",
    "Technique",
    "TekhnēRegistry",
    "STANDARD_TECHNIQUES",
    "get_registry",
    "search_techniques",
    "format_registry_markdown",
    # O4 Energeia
    "ExecutionPhase",
    "ExecutionStatus",
    "ExecutionContext",
    "ExecutionResult",
    "EnergеiaExecutor",
    "format_execution_markdown",
    "encode_execution_observation",
    # K2 Chronos
    "TimeScale",
    "CertaintyLevel",
    "SlackLevel",
    "ChronosResult",
    "evaluate_time",
    "format_chronos_markdown",
    "encode_chronos_observation",
]



