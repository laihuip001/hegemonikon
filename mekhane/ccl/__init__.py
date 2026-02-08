# PROOF: [L2/インフラ] <- mekhane/ccl/ CCL実行基盤
"""
CCL (Cognitive Control Language) Module v2.4

LLM-based intent-to-CCL conversion with 4-layer fallback:
  Layer 1: LLM (Primary)
  Layer 2: Doxa Patterns (Learned)
  Layer 3: Heuristic (Static)
  Layer 4: User Inquiry (Fallback)

v2.1: Macro system (@name), Level syntax (:N)
v2.2: Semantic validation layer
v2.3: Semantic matcher (Japanese→Macro), Workflow signatures
v2.4: Zero-Trust CCL Executor (5-phase enforcement)
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
from .workflow_signature import (
    SignatureRegistry,
    WorkflowSignature,
    WORKFLOW_SIGNATURES,
)

__all__ = [
    "LLMParser",
    "DoxaLearner",
    "PatternCache",
    "CCLSyntaxValidator",
    "ValidationResult",
    "CCLSemanticValidator",
    "SemanticResult",
    "validate_semantic",
    "CCLGenerator",
    "CCLTracer",
    "MacroRegistry",
    "MacroExpander",
    "Macro",
    "BUILTIN_MACROS",
    "SemanticMacroMatcher",
    "MacroMatch",
    "MACRO_DESCRIPTIONS_JP",
    "SignatureRegistry",
    "WorkflowSignature",
    "WORKFLOW_SIGNATURES",
    # Zero-Trust CCL Executor (v2.4)
    "ZeroTrustCCLExecutor",
    "create_ccl_prompt",
    "validate_ccl_output",
]


# Zero-Trust imports (lazy to avoid circular imports)
# PURPOSE: Get ZeroTrustCCLExecutor instance
def get_zero_trust_executor():
    """Get ZeroTrustCCLExecutor instance"""
    from .executor import ZeroTrustCCLExecutor

    return ZeroTrustCCLExecutor()


# PURPOSE: Create prompt with injected specs and warnings
def create_ccl_prompt(ccl_expr: str) -> str:
    """Create prompt with injected specs and warnings"""
    from .executor import create_ccl_prompt as _create

    return _create(ccl_expr)


# PURPOSE: Validate CCL output
def validate_ccl_output(ccl_expr: str, output: str):
    """Validate CCL output"""
    from .executor import validate_ccl_output as _validate

    return _validate(ccl_expr, output)
