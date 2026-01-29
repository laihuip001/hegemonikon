"""
CCL (Cognitive Control Language) Module v2.1

LLM-based intent-to-CCL conversion with 4-layer fallback:
  Layer 1: LLM (Primary)
  Layer 2: Doxa Patterns (Learned)
  Layer 3: Heuristic (Static)
  Layer 4: User Inquiry (Fallback)

v2.1: Macro system (@name), Level syntax (:N)
"""

from .llm_parser import LLMParser
from .doxa_learner import DoxaLearner
from .pattern_cache import PatternCache
from .syntax_validator import CCLSyntaxValidator, ValidationResult
from .generator import CCLGenerator
from .tracer import CCLTracer
from .macro_registry import MacroRegistry, Macro, BUILTIN_MACROS
from .macro_expander import MacroExpander

__all__ = [
    'LLMParser',
    'DoxaLearner',
    'PatternCache',
    'CCLSyntaxValidator',
    'ValidationResult',
    'CCLGenerator',
    'CCLTracer',
    'MacroRegistry',
    'MacroExpander',
    'Macro',
    'BUILTIN_MACROS',
]

