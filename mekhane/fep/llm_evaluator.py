# PROOF: [L2/インフラ] <- mekhane/fep/
"""
PROOF: このファイルは存在しなければならない

A0 → FEP には観察生成が必要
   → 正規表現だけでは不十分な場合がある
   → LLM による階層的評価が担う

Q.E.D.

---

LLM Evaluator - Hierarchical Hybrid Evaluation Layer

Implements the 3-layer evaluation architecture from /noe analysis:
- L1: Regex-based encode_input (cost=0)
- L2: Gemini 1.5 Flash free tier (cost=0)
- L3: Claude/GPT (on-demand, paid)

This module provides LLM-based observation generation when L1 confidence
is below threshold, using free APIs where possible.

References:
- arXiv:2412.10425: LLM as observation generator
- /noe analysis: Hierarchical Hybrid Evaluation
"""

from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass
import os
import json

# Check for available LLM clients
GEMINI_AVAILABLE = False
GEMINI_CLIENT = None
try:
    from google import genai

    GEMINI_AVAILABLE = True
except ImportError:
    pass  # TODO: Add proper error handling


@dataclass
class EvaluationResult:
    """Result from hierarchical evaluation."""

    observation: Tuple[int, int, int]  # (context, urgency, confidence)
    confidence: float  # Confidence in the evaluation (0-1)
    layer_used: str  # "L1", "L2", or "L3"
    raw_scores: Optional[Dict[str, float]] = None  # LLM evaluation scores
    interpretation: str = ""


# Evaluation thresholds
L1_CONFIDENCE_THRESHOLD = 0.75  # Below this, escalate to L2
L2_CONFIDENCE_THRESHOLD = 0.60  # Below this, escalate to L3

# Gemini model to use (free tier: gemini-2.0-flash-lite)
GEMINI_MODEL = "gemini-2.0-flash-lite"


# =============================================================================
# L1: Regex-based Evaluation with Confidence
# =============================================================================


def encode_input_with_confidence(text: str) -> Tuple[Tuple[int, int, int], float]:
    """L1: Encode input with confidence score.

    Extends encode_input() to also return a confidence score based on
    how many patterns were matched.

    Args:
        text: Natural language input

    Returns:
        Tuple of (observation_tuple, confidence_score)
        - observation_tuple: (context_idx, urgency_idx, confidence_idx)
        - confidence_score: 0.0-1.0 based on pattern match quality

    Example:
        >>> obs, conf = encode_input_with_confidence("緊急：ファイル.pyを修正して")
        >>> print(f"Confidence: {conf:.0%}")
        Confidence: 80%
    """
    from .encoding import (
        CONTEXT_PATTERNS,
        URGENCY_PATTERNS,
        CONFIDENCE_PATTERNS,
        encode_input,
    )
    import re

    # Get the observation tuple
    obs = encode_input(text)

    # Count matched patterns for confidence calculation
    total_patterns = 0
    matched_patterns = 0

    for category_patterns in [CONTEXT_PATTERNS, URGENCY_PATTERNS, CONFIDENCE_PATTERNS]:
        for level, patterns in category_patterns.items():
            for pattern in patterns:
                total_patterns += 1
                if re.search(pattern, text, re.IGNORECASE):
                    matched_patterns += 1

    # Length bonus for detailed inputs
    length_bonus = min(0.2, len(text) / 500)  # Up to 0.2 bonus for longer texts

    # Calculate confidence
    base_confidence = matched_patterns / max(1, total_patterns) * 3  # Normalize to ~1.0
    confidence = min(1.0, base_confidence + length_bonus)

    # Minimum confidence floor based on input length
    if len(text) > 50:
        confidence = max(confidence, 0.4)

    return obs, confidence


# =============================================================================
# L2: Gemini 1.5 Flash Evaluation (Free Tier)
# =============================================================================

GEMINI_EVALUATION_PROMPT = """あなたはActive Inference認知エージェントの観察生成器です。
以下のテキストを分析し、3つの次元で評価してください。

テキスト:
---
{text}
---

以下のJSON形式で回答してください（日本語説明不要、JSONのみ）:
{{
    "context_clarity": 0.0-1.0,  // 0=曖昧, 1=明確
    "urgency": 0.0-1.0,          // 0=低, 1=高
    "confidence": 0.0-1.0        // 入力者の確信度
}}"""


def evaluate_with_gemini(text: str) -> Optional[Dict[str, float]]:
    """L2: Evaluate text using Gemini Flash (free tier).

    Uses the free tier of Gemini API for observation generation.

    Args:
        text: Text to evaluate

    Returns:
        Dict with context_clarity, urgency, confidence scores,
        or None if evaluation fails
    """
    if not GEMINI_AVAILABLE:
        return None

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        # Use new google-genai Client API
        client = genai.Client(api_key=api_key)

        prompt = GEMINI_EVALUATION_PROMPT.format(text=text)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        # Parse JSON response
        response_text = response.text.strip()

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        scores = json.loads(response_text)

        # Validate scores
        for key in ["context_clarity", "urgency", "confidence"]:
            if key not in scores:
                return None
            scores[key] = max(0.0, min(1.0, float(scores[key])))

        return scores

    except Exception as e:
        # Log error but don't crash
        print(f"[L2 Gemini] Evaluation failed: {e}")
        return None


def scores_to_observation(scores: Dict[str, float]) -> Tuple[int, int, int]:
    """Convert LLM evaluation scores to observation indices.

    Args:
        scores: Dict with context_clarity, urgency, confidence (0-1)

    Returns:
        Tuple of (context_idx, urgency_idx, confidence_idx)
    """
    # Context: 2 levels
    context_idx = 1 if scores["context_clarity"] >= 0.5 else 0

    # Urgency: 3 levels
    if scores["urgency"] < 0.33:
        urgency_idx = 0
    elif scores["urgency"] < 0.66:
        urgency_idx = 1
    else:
        urgency_idx = 2

    # Confidence: 3 levels
    if scores["confidence"] < 0.33:
        confidence_idx = 0
    elif scores["confidence"] < 0.66:
        confidence_idx = 1
    else:
        confidence_idx = 2

    return (context_idx, urgency_idx, confidence_idx)


# =============================================================================
# Hierarchical Evaluation
# =============================================================================


def hierarchical_evaluate(
    text: str,
    force_layer: Optional[str] = None,
) -> EvaluationResult:
    """Perform hierarchical hybrid evaluation.

    Implements the 3-layer architecture:
    - L1: Regex (always runs, establishes baseline)
    - L2: Gemini (if L1 confidence < 0.75)
    - L3: Claude/GPT (if L2 confidence < 0.60) [not implemented yet]

    Args:
        text: Text to evaluate
        force_layer: Optional, force a specific layer ("L1", "L2", "L3")

    Returns:
        EvaluationResult with observation, confidence, and metadata

    Example:
        >>> result = hierarchical_evaluate("y")
        >>> print(f"Layer: {result.layer_used}, Confidence: {result.confidence:.0%}")
        Layer: L1, Confidence: 85%
    """
    # L1: Always run regex first
    l1_obs, l1_confidence = encode_input_with_confidence(text)

    # Force L1 if requested
    if force_layer == "L1":
        return EvaluationResult(
            observation=l1_obs,
            confidence=l1_confidence,
            layer_used="L1",
            interpretation=f"L1 regex evaluation (forced)",
        )

    # Check if L1 is sufficient
    if l1_confidence >= L1_CONFIDENCE_THRESHOLD and force_layer is None:
        return EvaluationResult(
            observation=l1_obs,
            confidence=l1_confidence,
            layer_used="L1",
            interpretation=f"L1 regex evaluation (confidence {l1_confidence:.0%} >= threshold)",
        )

    # L2: Escalate to Gemini
    if force_layer in (None, "L2"):
        gemini_scores = evaluate_with_gemini(text)

        if gemini_scores:
            l2_obs = scores_to_observation(gemini_scores)
            # L2 confidence is average of Gemini's reported confidence
            l2_confidence = (
                gemini_scores["context_clarity"] * 0.3
                + gemini_scores["confidence"] * 0.7
            )

            if l2_confidence >= L2_CONFIDENCE_THRESHOLD or force_layer == "L2":
                return EvaluationResult(
                    observation=l2_obs,
                    confidence=l2_confidence,
                    layer_used="L2",
                    raw_scores=gemini_scores,
                    interpretation=f"L2 Gemini evaluation (confidence {l2_confidence:.0%})",
                )

    # L3: Would escalate to Claude/GPT (not implemented)
    # For now, fall back to L1 with a warning
    return EvaluationResult(
        observation=l1_obs,
        confidence=l1_confidence,
        layer_used="L1",
        interpretation=f"L1 fallback (L2 unavailable or below threshold)",
    )


# =============================================================================
# Integration with FEP Agent
# =============================================================================


def evaluate_and_infer(
    text: str,
    agent: Optional[Any] = None,
) -> Dict[str, Any]:
    """Evaluate text and perform FEP inference in one call.

    Combines hierarchical evaluation with FEP agent inference.

    Args:
        text: Text to evaluate
        agent: Optional HegemonikónFEPAgent instance (creates one if not provided)

    Returns:
        Dict with evaluation_result, fep_result, and combined interpretation
    """
    from .fep_agent import HegemonikónFEPAgent
    from .encoding import decode_observation, generate_fep_feedback_markdown

    # Evaluate
    eval_result = hierarchical_evaluate(text)

    # Get or create agent
    if agent is None:
        agent = HegemonikónFEPAgent(use_defaults=True)

    # Compute flat observation index for FEP agent
    obs = eval_result.observation
    flat_obs = obs[0] + 2 * obs[1] + obs[2]

    # FEP inference
    fep_result = agent.step(flat_obs)

    # Generate combined output
    obs_description = f"context={'clear' if obs[0] else 'ambiguous'}, urgency={['low','med','high'][obs[1]]}, conf={['low','med','high'][obs[2]]}"
    fep_feedback = generate_fep_feedback_markdown(fep_result, obs_description)

    return {
        "evaluation": {
            "observation": eval_result.observation,
            "confidence": eval_result.confidence,
            "layer": eval_result.layer_used,
            "interpretation": eval_result.interpretation,
        },
        "fep": fep_result,
        "combined_feedback": f"""━━━ Hierarchical Evaluation ━━━
Layer: {eval_result.layer_used} (confidence {eval_result.confidence:.0%})
{eval_result.interpretation}

{fep_feedback}""",
    }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "encode_input_with_confidence",
    "evaluate_with_gemini",
    "hierarchical_evaluate",
    "evaluate_and_infer",
    "EvaluationResult",
    "GEMINI_AVAILABLE",
    "L1_CONFIDENCE_THRESHOLD",
    "L2_CONFIDENCE_THRESHOLD",
]
