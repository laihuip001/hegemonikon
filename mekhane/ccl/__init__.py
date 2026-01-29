"""
CCL (Cognitive Control Language) Module v2.0

LLM-based intent-to-CCL conversion with 4-layer fallback:
  Layer 1: LLM (Primary)
  Layer 2: Doxa Patterns (Learned)
  Layer 3: Heuristic (Static)
  Layer 4: User Inquiry (Fallback)
"""

from .llm_parser import LLMParser
from .doxa_learner import DoxaLearner
from .pattern_cache import PatternCache
from .syntax_validator import CCLSyntaxValidator, ValidationResult
from .generator import CCLGenerator
from .tracer import CCLTracer

__all__ = [
    'LLMParser',
    'DoxaLearner',
    'PatternCache',
    'CCLSyntaxValidator',
    'ValidationResult',
    'CCLGenerator',
    'CCLTracer',
]
