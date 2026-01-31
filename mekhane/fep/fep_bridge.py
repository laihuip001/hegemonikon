# PROOF: [L2/インフラ]
"""
PROOF: [L1/定理] このファイルは存在しなければならない

A0 → FEP エージェントが存在する (fep_agent.py)
   → ワークフローとの統合が必要
   → 高レベル API を提供する橋渡し層が担う

Q.E.D.

---

FEP Bridge - Workflow Integration Layer

Provides high-level functions for invoking FEP capabilities from
Hegemonikón workflows (/noe, /bou).

This bridge abstracts the pymdp agent complexity and provides
workflow-friendly return values that can be directly embedded
in workflow outputs.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import numpy as np

try:
    from .fep_agent import HegemonikónFEPAgent, PYMDP_AVAILABLE
except ImportError:
    from mekhane.fep.fep_agent import HegemonikónFEPAgent, PYMDP_AVAILABLE


@dataclass
class NoesisResult:
    """Result from O1 Noēsis FEP analysis."""
    
    entropy: float
    confidence: float  # 1 - normalized_entropy
    map_state: Dict[str, str]
    interpretation: str
    raw_beliefs: Optional[np.ndarray] = None


@dataclass
class BoulesisResult:
    """Result from O2 Boulēsis FEP analysis."""
    
    preferred_action: int
    action_name: str
    action_probabilities: List[float]
    expected_free_energy: List[float]
    interpretation: str


# Singleton agent instance (lazy initialization)
_agent: Optional[HegemonikónFEPAgent] = None


def _get_agent() -> HegemonikónFEPAgent:
    """Get or create the singleton FEP agent."""
    global _agent
    if _agent is None:
        if not PYMDP_AVAILABLE:
            raise ImportError(
                "pymdp is not installed. Install with: pip install pymdp"
            )
        _agent = HegemonikónFEPAgent(use_defaults=True)
    return _agent


def noesis_analyze(
    context_clarity: int = 1,
    reset_beliefs: bool = False,
) -> NoesisResult:
    """O1 Noēsis: Analyze cognitive state using Active Inference.
    
    Maps to PHASE 5 of /noe workflow, providing:
    - Belief entropy (uncertainty measure)
    - Confidence score (1 - normalized entropy)
    - MAP state interpretation
    
    Args:
        context_clarity: Observation index (0=unclear, 1=somewhat_clear, 2=clear)
        reset_beliefs: If True, reset agent beliefs before analysis
        
    Returns:
        NoesisResult with entropy, confidence, and interpretation
        
    Example:
        >>> result = noesis_analyze(context_clarity=2)
        >>> print(f"Confidence: {result.confidence:.0%}")
        >>> print(result.interpretation)
    """
    agent = _get_agent()
    
    if reset_beliefs:
        agent.reset()
    
    # Perform state inference
    inference_result = agent.infer_states(context_clarity)
    
    # Calculate normalized entropy (0-1 scale)
    max_entropy = np.log(agent.state_dim)  # Maximum entropy for uniform distribution
    normalized_entropy = inference_result["entropy"] / max_entropy if max_entropy > 0 else 0
    
    # Confidence is inverse of normalized entropy
    confidence = 1.0 - normalized_entropy
    
    # Generate interpretation
    map_state = inference_result["map_state_names"]
    interpretation = _interpret_noesis_state(map_state, confidence)
    
    return NoesisResult(
        entropy=inference_result["entropy"],
        confidence=confidence,
        map_state=map_state,
        interpretation=interpretation,
        raw_beliefs=inference_result["beliefs"],
    )


def boulesis_analyze(
    prior_noesis: Optional[NoesisResult] = None,
) -> BoulesisResult:
    """O2 Boulēsis: Select optimal action using Expected Free Energy.
    
    Maps to PHASE 5 of /bou workflow, providing:
    - Policy probabilities
    - Preferred action
    - EFE-based interpretation
    
    Args:
        prior_noesis: Optional result from noesis_analyze to chain inferences
        
    Returns:
        BoulesisResult with action probabilities and interpretation
        
    Example:
        >>> noe_result = noesis_analyze(context_clarity=1)
        >>> bou_result = boulesis_analyze(prior_noesis=noe_result)
        >>> print(f"Recommended: {bou_result.action_name}")
    """
    agent = _get_agent()
    
    # If no prior noesis, perform state inference first
    if prior_noesis is None:
        agent.infer_states(1)  # Default: somewhat clear context
    
    # Perform policy inference
    q_pi, neg_efe = agent.infer_policies()
    
    # Handle array outputs
    if isinstance(q_pi, np.ndarray):
        q_pi = q_pi.flatten().tolist()
    if isinstance(neg_efe, np.ndarray):
        neg_efe = neg_efe.flatten().tolist()
    
    # Sample action
    action = agent.sample_action()
    
    # Action names
    action_names = ["observe", "act"]
    action_name = action_names[action] if action < len(action_names) else f"action_{action}"
    
    # Generate interpretation
    interpretation = _interpret_boulesis_policy(q_pi, action_name)
    
    return BoulesisResult(
        preferred_action=action,
        action_name=action_name,
        action_probabilities=q_pi,
        expected_free_energy=[-e for e in neg_efe],  # Convert neg_efe to EFE
        interpretation=interpretation,
    )


def full_inference_cycle(
    context_clarity: int = 1,
    reset_beliefs: bool = True,
) -> Dict[str, Any]:
    """Complete O1→O2 inference cycle.
    
    Performs both Noēsis (state inference) and Boulēsis (policy selection)
    in sequence, returning combined results suitable for workflow output.
    
    Args:
        context_clarity: Observation index (0=unclear, 1=somewhat_clear, 2=clear)
        reset_beliefs: If True, reset agent beliefs before analysis
        
    Returns:
        Dict with 'noesis' and 'boulesis' results, plus 'summary'
    """
    # O1 Noēsis
    noesis_result = noesis_analyze(
        context_clarity=context_clarity,
        reset_beliefs=reset_beliefs,
    )
    
    # O2 Boulēsis (chained from Noēsis)
    boulesis_result = boulesis_analyze(prior_noesis=noesis_result)
    
    # Generate summary
    summary = _generate_fep_summary(noesis_result, boulesis_result)
    
    return {
        "noesis": {
            "entropy": noesis_result.entropy,
            "confidence": noesis_result.confidence,
            "map_state": noesis_result.map_state,
            "interpretation": noesis_result.interpretation,
        },
        "boulesis": {
            "preferred_action": boulesis_result.preferred_action,
            "action_name": boulesis_result.action_name,
            "action_probabilities": boulesis_result.action_probabilities,
            "interpretation": boulesis_result.interpretation,
        },
        "summary": summary,
    }


def _interpret_noesis_state(map_state: Dict[str, str], confidence: float) -> str:
    """Generate human-readable interpretation of Noēsis result."""
    phantasia = map_state.get("phantasia", "unknown")
    assent = map_state.get("assent", "unknown")
    horme = map_state.get("horme", "unknown")
    
    conf_level = "高" if confidence > 0.7 else "中" if confidence > 0.4 else "低"
    
    return (
        f"[FEP Noēsis] 認識状態: phantasia={phantasia}, "
        f"syncatasthesis={assent}, hormē={horme} | "
        f"信念確信度: {conf_level} ({confidence:.0%})"
    )


def _interpret_boulesis_policy(q_pi: List[float], action_name: str) -> str:
    """Generate human-readable interpretation of Boulēsis result."""
    if len(q_pi) >= 2:
        observe_prob = q_pi[0]
        act_prob = q_pi[1]
        
        if observe_prob > act_prob:
            recommendation = "追加情報収集を推奨"
        else:
            recommendation = "行動実行を推奨"
        
        return (
            f"[FEP Boulēsis] 政策分布: observe={observe_prob:.0%}, act={act_prob:.0%} | "
            f"選択: {action_name} | {recommendation}"
        )
    
    return f"[FEP Boulēsis] 選択: {action_name}"


def _generate_fep_summary(
    noesis: NoesisResult,
    boulesis: BoulesisResult,
) -> str:
    """Generate combined FEP analysis summary."""
    return (
        f"━━━ FEP Analysis ━━━\n"
        f"O1 Noēsis: 信念エントロピー {noesis.entropy:.3f} (確信度 {noesis.confidence:.0%})\n"
        f"O2 Boulēsis: {boulesis.action_name} (EFE最小化)\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )


# Public API
__all__ = [
    "noesis_analyze",
    "boulesis_analyze", 
    "full_inference_cycle",
    "NoesisResult",
    "BoulesisResult",
    "PYMDP_AVAILABLE",
]
