"""
Text-to-Observation Encoding for Hegemonikón Active Inference

Converts natural language input into observation indices for the FEP agent.

Observation modalities:
- context: [ambiguous, clear] → 2 values
- urgency: [low, medium, high] → 3 values
- confidence: [low, medium, high] → 3 values

References:
- Anti-Skip Protocol (context clarity)
- K-series Kairos (urgency)
- A-series Akribeia (confidence)
"""

from typing import Dict, Tuple, Optional, List
import re

from .state_spaces import OBSERVATION_MODALITIES


# =============================================================================
# Keyword Patterns for Analysis
# =============================================================================

# Context clarity indicators (Anti-Skip Protocol)
CONTEXT_PATTERNS: Dict[str, List[str]] = {
    "clear": [
        r"(明確|具体的|はっきり|clear|specific|detailed|explicitly)",
        r"(ファイル|パス|コード|関数|クラス)",  # References to specific code
        r"\.py",  # Python files
        r"```",  # Code blocks indicate specificity
        r"file://",  # File paths
    ],
    "ambiguous": [
        r"(なんか|何か|どう|なに|something|somehow|maybe)",
        r"(曖昧|不明|unclear|vague|uncertain)",
        r"\?{2,}",  # Multiple question marks
        r"^\s*\?\s*$",  # Just a question mark
    ],
}

# Urgency indicators (K-series Kairos)
URGENCY_PATTERNS: Dict[str, List[str]] = {
    "high": [
        r"(緊急|急ぎ|すぐに|今すぐ|urgent|asap|immediately|now)",
        r"(deadline|期限|締め切り)",
        r"!{2,}",  # Multiple exclamation marks
        r"(バグ|エラー|壊れ|crashed|broken|error|bug)",
    ],
    "medium": [
        r"(早め|できれば|soon|when.*possible)",
        r"(今日|本日|today)",
    ],
    "low": [
        r"(いつでも|余裕|eventually|whenever|later)",
        r"(アイデア|検討|考え|think|consider|explore)",
    ],
}

# Confidence indicators (A-series Akribeia)
CONFIDENCE_PATTERNS: Dict[str, List[str]] = {
    "high": [
        r"^\s*y\s*$",  # Simple "y" approval
        r"\b(はい|yes|確信|certain|definitely|承認|approve)\b",
        r"\b(やって|実行|do it|execute|proceed)\b",
    ],
    "medium": [
        r"\b(たぶん|おそらく|probably|maybe|think so)\b",
        r"\b(続けよう|continue|進めよう)\b",
    ],
    "low": [
        r"\b(わからない|不明|unsure|don't know|unclear)\b",
        r"\b(どう思う|what do you think|意見|opinion)\b",
        r"\?$",  # Ends with question mark
    ],
}


# =============================================================================
# Encoding Functions
# =============================================================================

def analyze_context(text: str) -> str:
    """Analyze text for context clarity.
    
    Args:
        text: Input text to analyze
        
    Returns:
        'clear' or 'ambiguous'
    """
    clear_score = 0
    ambiguous_score = 0
    
    for pattern in CONTEXT_PATTERNS["clear"]:
        if re.search(pattern, text, re.IGNORECASE):
            clear_score += 1
    
    for pattern in CONTEXT_PATTERNS["ambiguous"]:
        if re.search(pattern, text, re.IGNORECASE):
            ambiguous_score += 1
    
    # Length heuristic: longer messages tend to be clearer
    if len(text) > 100:
        clear_score += 1
    
    return "clear" if clear_score > ambiguous_score else "ambiguous"


def analyze_urgency(text: str) -> str:
    """Analyze text for urgency level.
    
    Args:
        text: Input text to analyze
        
    Returns:
        'low', 'medium', or 'high'
    """
    scores = {"low": 0, "medium": 0, "high": 0}
    
    for level, patterns in URGENCY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores[level] += 1
    
    # Default to low if no patterns match
    if sum(scores.values()) == 0:
        return "low"
    
    return max(scores, key=scores.get)


def analyze_confidence(text: str) -> str:
    """Analyze text for confidence level.
    
    Args:
        text: Input text to analyze
        
    Returns:
        'low', 'medium', or 'high'
    """
    scores = {"low": 0, "medium": 0, "high": 0}
    
    for level, patterns in CONFIDENCE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores[level] += 1
    
    # Default to medium if no patterns match
    if sum(scores.values()) == 0:
        return "medium"
    
    return max(scores, key=scores.get)


def encode_input(text: str) -> Tuple[int, int, int]:
    """Convert text input to observation indices.
    
    This is the main entry point for text-to-observation encoding.
    
    Args:
        text: Natural language input
        
    Returns:
        Tuple of observation indices:
        - context_idx: 0 (ambiguous) or 1 (clear)
        - urgency_idx: 0 (low), 1 (medium), or 2 (high)
        - confidence_idx: 0 (low), 1 (medium), or 2 (high)
    
    Example:
        >>> encode_input("緊急：ファイルを修正して")
        (1, 2, 1)  # clear context, high urgency, medium confidence
        
        >>> encode_input("y")
        (0, 0, 2)  # ambiguous context, low urgency, high confidence
    """
    context = analyze_context(text)
    urgency = analyze_urgency(text)
    confidence = analyze_confidence(text)
    
    # Convert to indices
    context_idx = OBSERVATION_MODALITIES["context"].index(context)
    urgency_idx = OBSERVATION_MODALITIES["urgency"].index(urgency)
    confidence_idx = OBSERVATION_MODALITIES["confidence"].index(confidence)
    
    return (context_idx, urgency_idx, confidence_idx)


def encode_to_flat_index(text: str) -> int:
    """Convert text input to flat observation index.
    
    For use with single-modality pymdp agents.
    
    Args:
        text: Natural language input
        
    Returns:
        Flat observation index (0-7)
    """
    context_idx, urgency_idx, confidence_idx = encode_input(text)
    
    # Compute flat index (context * 6 + urgency * 3 + confidence)
    # But current A matrix uses: context(2) + urgency(3) + confidence(3) = 8
    # So we return the primary indicator based on context
    return context_idx + 2 * urgency_idx + confidence_idx


def decode_observation(obs: Tuple[int, int, int]) -> Dict[str, str]:
    """Convert observation indices back to human-readable format.
    
    Args:
        obs: Tuple of (context_idx, urgency_idx, confidence_idx)
        
    Returns:
        Dict with human-readable observation values
    """
    return {
        "context": OBSERVATION_MODALITIES["context"][obs[0]],
        "urgency": OBSERVATION_MODALITIES["urgency"][obs[1]],
        "confidence": OBSERVATION_MODALITIES["confidence"][obs[2]],
    }


# =============================================================================
# Structured Input Encoding
# =============================================================================

def encode_structured_input(
    context: Optional[str] = None,
    urgency: Optional[str] = None,
    confidence: Optional[str] = None,
) -> Tuple[int, int, int]:
    """Encode explicitly specified observation values.
    
    Use this when observation values are known programmatically
    rather than needing to be inferred from text.
    
    Args:
        context: 'ambiguous' or 'clear' (default: 'ambiguous')
        urgency: 'low', 'medium', or 'high' (default: 'low')
        confidence: 'low', 'medium', or 'high' (default: 'medium')
        
    Returns:
        Tuple of observation indices
    """
    context = context or "ambiguous"
    urgency = urgency or "low"
    confidence = confidence or "medium"
    
    context_idx = OBSERVATION_MODALITIES["context"].index(context)
    urgency_idx = OBSERVATION_MODALITIES["urgency"].index(urgency)
    confidence_idx = OBSERVATION_MODALITIES["confidence"].index(confidence)
    
    return (context_idx, urgency_idx, confidence_idx)
