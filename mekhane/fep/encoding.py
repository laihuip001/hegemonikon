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


# =============================================================================
# FEP with Learning & Persistence
# =============================================================================

def run_fep_with_learning(
    obs_tuple: Tuple[int, int, int],
    a_matrix_path: str = "/home/laihuip001/oikos/mneme/.hegemonikon/fep/learned_A.npy",
    learning_rate: float = 50.0,
) -> Dict:
    """Execute FEP inference + Dirichlet learning + persistence in one flow.
    
    This function handles the complete FEP cycle:
    1. Load learned A-matrix (if exists)
    2. Run inference step
    3. Update A-matrix with Dirichlet learning
    4. Save updated A-matrix
    
    Args:
        obs_tuple: Observation tuple (context_idx, urgency_idx, confidence_idx)
        a_matrix_path: Path to save/load learned A-matrix
        learning_rate: Dirichlet update learning rate (default: 50.0)
    
    Returns:
        Dict with step() results + should_epoche flag
    
    Example:
        >>> from mekhane.fep.encoding import encode_noesis_output, run_fep_with_learning
        >>> obs = encode_noesis_output(0.85, [{"zone": "A"}])
        >>> result = run_fep_with_learning(obs)
        >>> print(result["action_name"], result["should_epoche"])
    """
    from mekhane.fep import HegemonikónFEPAgent
    import os
    
    agent = HegemonikónFEPAgent(use_defaults=True)
    
    # 1. Load learned A-Matrix if exists
    agent.load_learned_A(a_matrix_path)
    
    # 2. Run inference
    flat_obs = obs_tuple[0] + 2 * obs_tuple[1] + obs_tuple[2]
    result = agent.step(observation=flat_obs)
    
    # 3. Dirichlet update
    agent.update_A_dirichlet(observation=flat_obs, learning_rate=learning_rate)
    
    # 4. Save
    os.makedirs(os.path.dirname(a_matrix_path), exist_ok=True)
    agent.save_learned_A(a_matrix_path)
    
    # 5. Add Auto-Epochē flag
    result["should_epoche"] = result.get("entropy", 0) >= 2.0
    
    return result


def should_trigger_epoche(agent_result: Dict, threshold: float = 2.0) -> bool:
    """Check if Epochē should be triggered based on entropy.
    
    High entropy indicates high uncertainty in beliefs, suggesting
    that judgment should be suspended (/epo).
    
    Args:
        agent_result: Result dict from HegemonikónFEPAgent.step()
        threshold: Entropy threshold (default: 2.0)
    
    Returns:
        True if entropy >= threshold (Epochē recommended)
    
    Example:
        >>> if should_trigger_epoche(result):
        ...     print("⚠️ 高エントロピー → /epo 推奨")
    """
    return agent_result.get("entropy", 0.0) >= threshold


# =============================================================================
# Feature 3: Auto-Encode Noēsis (PHASE 5 自動変換)
# =============================================================================

def auto_encode_noesis(phase5_output: dict) -> Tuple[int, int, int]:
    """PHASE 5 JSON 出力を FEP 観察に自動変換.
    
    /noe ワークフローの PHASE 5 出力を受け取り、
    FEP Agent 用の観察値に自動変換する。
    
    Args:
        phase5_output: PHASE 5 の構造化出力 (JSON)
            必須キー: confidence_score, uncertainty_zones
    
    Returns:
        Tuple of (context_idx, urgency_idx, confidence_idx)
    
    Example:
        >>> phase5 = {"confidence_score": 0.78, "uncertainty_zones": [{"zone": "A"}]}
        >>> auto_encode_noesis(phase5)
        (1, 0, 2)  # clear, low, high
    """
    confidence = phase5_output.get("confidence_score", 0.5)
    zones = phase5_output.get("uncertainty_zones", [])
    return encode_noesis_output(confidence, zones)


# =============================================================================
# Feature 2: Learning Progress Visualization
# =============================================================================

def format_learning_progress(
    before_A: Optional["np.ndarray"] = None,
    after_A: Optional["np.ndarray"] = None,
    observation: Optional[Tuple[int, int, int]] = None,
    inference_count: int = 1,
) -> str:
    """A行列の学習進捗を Markdown で可視化.
    
    FEP Agent の観察モデル (A行列) がどのように更新されたかを
    人間が読める形式で表示する。
    
    Args:
        before_A: 更新前の A行列 (optional)
        after_A: 更新後の A行列 (optional)
        observation: 今回の観察値 (optional)
        inference_count: 累計推論回数
    
    Returns:
        Markdown formatted learning progress
    
    Example:
        >>> print(format_learning_progress(inference_count=5))
        ┌─[FEP Learning Progress]─────────────────────┐
        │ 推論回数: 5                                  │
        │ A行列更新: なし (before/after 未提供)        │
        └──────────────────────────────────────────────┘
    """
    lines = [
        "┌─[FEP Learning Progress]─────────────────────┐",
        f"│ 推論回数: {inference_count}",
    ]
    
    if observation:
        obs_decoded = decode_observation(observation)
        lines.append(
            f"│ 観察値: context={obs_decoded['context']}, "
            f"urgency={obs_decoded['urgency']}, conf={obs_decoded['confidence']}"
        )
    
    if before_A is not None and after_A is not None:
        try:
            import numpy as np
            delta = np.abs(after_A - before_A).sum()
            lines.append(f"│ A行列変化量: {delta:.4f}")
            if delta > 0.01:
                lines.append("│ 📈 有意な学習が発生")
            else:
                lines.append("│ 📊 安定状態（微小変化）")
        except ImportError:
            lines.append("│ A行列変化: numpy 未インポート")
    else:
        lines.append("│ A行列更新: なし (before/after 未提供)")
    
    lines.append("└──────────────────────────────────────────────┘")
    return "\n".join(lines)


# =============================================================================
# Feature 1: X-Series Navigation Constants
# =============================================================================

# X-series 36関係マトリクス定義
X_SERIES_MATRIX = {
    "O": {"O": "X-OO", "S": "X-OS", "H": "X-OH", "P": "X-OP", "K": "X-OK", "A": "X-OA"},
    "S": {"O": "X-SO", "S": "X-SS", "H": "X-SH", "P": "X-SP", "K": "X-SK", "A": "X-SA"},
    "H": {"O": "X-HO", "S": "X-HS", "H": "X-HH", "P": "X-HP", "K": "X-HK", "A": "X-HA"},
    "P": {"O": "X-PO", "S": "X-PS", "H": "X-PH", "P": "X-PP", "K": "X-PK", "A": "X-PA"},
    "K": {"O": "X-KO", "S": "X-KS", "H": "X-KH", "P": "X-KP", "K": "X-KK", "A": "X-KA"},
    "A": {"O": "X-AO", "S": "X-AS", "H": "X-AH", "P": "X-AP", "K": "X-AK", "A": "X-AA"},
}

# 代表的な遷移経路
X_SERIES_REPRESENTATIVE_PATHS = {
    "X-OS": ("O1", "S1"),  # 認識→スケール
    "X-OA": ("O1", "A2"),  # 認識→検証
    "X-OH": ("O1", "H1"),  # 認識→傾向
    "X-OP": ("O4", "P4"),  # 行為→技法
    "X-SO": ("S4", "O4"),  # 実践→行為
    "X-HO": ("H2", "O4"),  # 確信→行為
    "X-KO": ("K4", "O1"),  # 知恵→認識
    "X-AO": ("A4", "O1"),  # 知識→認識
}


def get_x_series_recommendations(
    current_series: str,
    confidence: float = 0.5,
) -> List[Dict[str, str]]:
    """現在のシリーズから X-series 推奨次ステップを取得.
    
    Args:
        current_series: 現在のシリーズ (O, S, H, P, K, A)
        confidence: 現在の確信度 (0.0-1.0)
    
    Returns:
        List of recommendation dicts with keys: x_id, target, workflow, reason
    
    Example:
        >>> get_x_series_recommendations("O", 0.78)
        [{'x_id': 'X-OS', 'target': 'S', 'workflow': '/s', 'reason': '認識→設計へ'}, ...]
    """
    WORKFLOW_MAP = {
        "O": "/noe", "S": "/s", "H": "/pro", 
        "P": "/kho", "K": "/euk", "A": "/dia"
    }
    REASON_MAP = {
        "O": "本質", "S": "設計", "H": "傾向",
        "P": "環境", "K": "文脈", "A": "検証"
    }
    
    if current_series not in X_SERIES_MATRIX:
        return []
    
    recommendations = []
    connections = X_SERIES_MATRIX[current_series]
    
    # 高確信 → 行動系 (S, P) を優先
    # 低確信 → 検証系 (A, K) を優先
    if confidence >= 0.7:
        priority = ["S", "P", "O", "H", "K", "A"]
    else:
        priority = ["A", "K", "S", "O", "H", "P"]
    
    for target in priority[:3]:  # 上位3つ
        if target == current_series:
            continue
        x_id = connections[target]
        recommendations.append({
            "x_id": x_id,
            "target": target,
            "workflow": WORKFLOW_MAP.get(target, f"/{target.lower()}"),
            "reason": f"{REASON_MAP.get(current_series, current_series)}→{REASON_MAP.get(target, target)}へ",
        })
    
    return recommendations

