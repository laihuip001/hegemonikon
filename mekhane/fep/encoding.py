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


# =============================================================================
# Workflow Output Encoding
# =============================================================================

def encode_noesis_output(
    confidence_score: float,
    uncertainty_zones: List[Dict],
) -> Tuple[int, int, int]:
    """Encode O1 Noēsis PHASE 5 output to observation indices.
    
    Converts the structured output from Noēsis (deep thinking) workflow
    into observation indices for the FEP agent.
    
    Args:
        confidence_score: Confidence level from PHASE 5 (0.0-1.0)
        uncertainty_zones: List of uncertainty zone dicts from PHASE 5
    
    Returns:
        Tuple of (context_idx, urgency_idx, confidence_idx)
    
    Mapping Logic:
        - context_clarity = 1.0 - (len(uncertainty_zones) * 0.2)
          More uncertainty zones → more ambiguous context
        - urgency = 'low' (Noēsis is a deliberative process)
        - confidence = mapped from confidence_score
    
    Example:
        >>> encode_noesis_output(0.87, [{"zone": "A", "doubt_score": 0.4}])
        (1, 0, 2)  # clear context, low urgency, high confidence
    """
    # Context clarity: more uncertainty zones = more ambiguous
    context_clarity = max(0.0, min(1.0, 1.0 - len(uncertainty_zones) * 0.2))
    
    # Map to categorical values
    context = "clear" if context_clarity >= 0.5 else "ambiguous"
    urgency = "low"  # Noēsis is always deliberative, low urgency
    
    if confidence_score >= 0.7:
        confidence = "high"
    elif confidence_score >= 0.4:
        confidence = "medium"
    else:
        confidence = "low"
    
    return encode_structured_input(context=context, urgency=urgency, confidence=confidence)


def encode_boulesis_output(
    impulse_score: float,
    feasibility_score: float,
) -> Tuple[int, int, int]:
    """Encode O2 Boulēsis PHASE 5 output to observation indices.
    
    Converts the structured output from Boulēsis (will clarification) workflow
    into observation indices for the FEP agent.
    
    Args:
        impulse_score: Impulse score (0-100), higher = more impulsive
        feasibility_score: Feasibility score (0-100)
    
    Returns:
        Tuple of (context_idx, urgency_idx, confidence_idx)
    
    Mapping Logic:
        - context = based on feasibility (>=50 = clear)
        - urgency = based on impulse score (high impulse = high urgency)
        - confidence = based on feasibility score
    
    Example:
        >>> encode_boulesis_output(impulse_score=25, feasibility_score=80)
        (1, 0, 2)  # clear context, low urgency (deliberate), high confidence
    """
    # Urgency from impulse: high impulse → high urgency
    if impulse_score >= 70:
        urgency = "high"
    elif impulse_score >= 40:
        urgency = "medium"
    else:
        urgency = "low"
    
    # Confidence from feasibility
    if feasibility_score >= 70:
        confidence = "high"
    elif feasibility_score >= 40:
        confidence = "medium"
    else:
        confidence = "low"
    
    # Context clarity from feasibility
    context = "clear" if feasibility_score >= 50 else "ambiguous"
    
    return encode_structured_input(context=context, urgency=urgency, confidence=confidence)


def generate_fep_feedback_markdown(
    agent_result: Dict,
    observation_description: str,
) -> str:
    """Generate Markdown-formatted FEP cognitive feedback.
    
    Creates a human-readable summary of the FEP agent's analysis,
    suitable for inclusion in workflow outputs.
    
    Args:
        agent_result: Result dict from HegemonikónFEPAgent.step()
        observation_description: Human-readable observation description
            e.g., "context=clear, urgency=low, conf=high"
    
    Returns:
        Markdown-formatted FEP feedback block
    
    Example:
        >>> result = agent.step(observation=0)
        >>> print(generate_fep_feedback_markdown(result, "context=clear"))
        ━━━ FEP Cognitive Feedback ━━━
        ┌─[Active Inference Layer]──────────────────┐
        │ 観察値: context=clear                      │
        ...
    """
    # Extract values with safe defaults
    action_name = agent_result.get("action_name", "unknown")
    action = agent_result.get("action", 0)
    q_pi = agent_result.get("q_pi", [0.5, 0.5])
    entropy = agent_result.get("entropy", 0.0)
    map_state = agent_result.get("map_state_names", {})
    
    # Calculate action probability
    if isinstance(q_pi, (list, tuple)) and len(q_pi) > action:
        action_prob = q_pi[action] * 100
    else:
        action_prob = 50.0
    
    # Interpret entropy
    if entropy < 1.0:
        entropy_desc = "低い不確実性"
    elif entropy < 2.0:
        entropy_desc = "中程度の不確実性"
    else:
        entropy_desc = "高い不確実性 (Epochē 推奨)"
    
    # Extract belief states
    phantasia = map_state.get("phantasia", "?")
    assent = map_state.get("assent", "?")
    horme = map_state.get("horme", "?")
    
    # Generate action guidance
    if action_name == "act":
        guidance = "→ 結論に確信あり、行動に移行可能"
    elif action_name == "observe":
        guidance = "→ 追加調査 (/zet) または判断停止 (/epo) を推奨"
    else:
        guidance = f"→ {action_name}"
    
    return f"""━━━ FEP Cognitive Feedback ━━━
┌─[Active Inference Layer]──────────────────┐
│ 観察値: {observation_description}
│ 信念状態:
│   phantasia: {phantasia}
│   assent: {assent}
│   horme: {horme}
│ エントロピー: {entropy:.2f} ({entropy_desc})
│ 推奨: {action_name} ({action_prob:.0f}%)
│   {guidance}
└────────────────────────────────────────────┘"""
