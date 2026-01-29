"""
CCL Generator v2.0

Main entry point for intent-to-CCL conversion.
Implements 4-layer fallback architecture:
  Layer 1: LLM (Primary)
  Layer 2: Doxa Patterns (Learned)
  Layer 3: Heuristic (Static)
  Layer 4: User Inquiry (Fallback)
"""

from typing import Optional, Tuple
from dataclasses import dataclass

from .llm_parser import LLMParser
from .doxa_learner import DoxaLearner
from .pattern_cache import PatternCache
from .syntax_validator import CCLSyntaxValidator


@dataclass
class GenerationResult:
    """Result of CCL generation."""
    ccl: str
    source: str  # "llm", "doxa", "heuristic", "user"
    confidence: float
    warnings: list


class CCLGenerator:
    """
    CCL Generator with 4-layer fallback.
    
    Converts natural language intent into CCL v2.0 expressions.
    """
    
    def __init__(self, enable_learning: bool = True):
        """
        Initialize the generator.
        
        Args:
            enable_learning: Whether to record successful conversions to Doxa
        """
        self.llm = LLMParser()
        self.doxa = DoxaLearner()
        self.heuristic = PatternCache()
        self.validator = CCLSyntaxValidator()
        self.enable_learning = enable_learning
    
    def generate(self, intent: str) -> GenerationResult:
        """
        Generate CCL from natural language intent.
        
        Args:
            intent: Natural language description of desired action
            
        Returns:
            GenerationResult with CCL expression and metadata
        """
        # Layer 1: LLM
        if self.llm.is_available():
            ccl = self.llm.parse(intent)
            if ccl:
                validation = self.validator.validate(ccl)
                if validation.valid:
                    if self.enable_learning:
                        self.doxa.record(intent, ccl, confidence=0.9)
                    return GenerationResult(
                        ccl=ccl,
                        source="llm",
                        confidence=0.9,
                        warnings=validation.warnings
                    )
        
        # Layer 2: Doxa Patterns
        cached = self.doxa.lookup(intent)
        if cached:
            validation = self.validator.validate(cached)
            if validation.valid:
                return GenerationResult(
                    ccl=cached,
                    source="doxa",
                    confidence=0.8,
                    warnings=validation.warnings
                )
        
        # Layer 3: Heuristic
        heuristic_ccl = self.heuristic.generate(intent)
        if heuristic_ccl:
            validation = self.validator.validate(heuristic_ccl)
            if validation.valid:
                if self.enable_learning:
                    self.doxa.record(intent, heuristic_ccl, confidence=0.6)
                return GenerationResult(
                    ccl=heuristic_ccl,
                    source="heuristic",
                    confidence=0.6,
                    warnings=validation.warnings
                )
        
        # Layer 4: User Inquiry
        return GenerationResult(
            ccl="/u",
            source="user",
            confidence=0.0,
            warnings=["Could not generate CCL - asking user"]
        )


# Convenience function for backward compatibility
def generate_ccl(intent: str) -> str:
    """
    Generate CCL from intent (simple interface).
    
    Args:
        intent: Natural language intent
        
    Returns:
        CCL expression string
    """
    generator = CCLGenerator()
    result = generator.generate(intent)
    return result.ccl
