"""
CCL (Cognitive Control Language) Module v2.3

LLM-based intent-to-CCL conversion with 4-layer fallback:
  Layer 1: LLM (Primary)
  Layer 2: Doxa Patterns (Learned)
  Layer 3: Heuristic (Static)
  Layer 4: User Inquiry (Fallback)

v2.1: Macro system (@name), Level syntax (:N)
v2.2: Semantic validation layer
v2.3: Semantic matcher (Japanese→Macro), Workflow signatures
"""

from .llm_parser import LLMParser
from .doxa_learner import DoxaLearner
from .pattern_cache import PatternCache
from .syntax_validator import CCLSyntaxValidator, ValidationResult
from .semantic_validator import CCLSemanticValidator, SemanticResult, validate_semantic
from .generator import CCLGenerator
from .tracer import CCLTracer
from .macro_registry import MacroRegistry, Macro, BUILTIN_MACROS
from .macro_expander import MacroExpander
from .semantic_matcher import SemanticMacroMatcher, MacroMatch, MACRO_DESCRIPTIONS_JP
from .workflow_signature import SignatureRegistry, WorkflowSignature, WORKFLOW_SIGNATURES

__all__ = [
    'LLMParser',
    'DoxaLearner',
    'PatternCache',
    'CCLSyntaxValidator',
    'ValidationResult',
    'CCLSemanticValidator',
    'SemanticResult',
    'validate_semantic',
    'CCLGenerator',
    'CCLTracer',
    'MacroRegistry',
    'MacroExpander',
    'Macro',
    'BUILTIN_MACROS',
    'SemanticMacroMatcher',
    'MacroMatch',
    'MACRO_DESCRIPTIONS_JP',
    'SignatureRegistry',
    'WorkflowSignature',
    'WORKFLOW_SIGNATURES',
]

