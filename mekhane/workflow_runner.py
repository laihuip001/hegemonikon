"""
Workflow Runner with Derivative Selection

Hegemonikón ワークフロー実行時に派生選択を自動実行するオーケストレーター。

Usage:
    from mekhane.workflow_runner import run_workflow
    
    result = run_workflow("O1", "この問題の本質は何か")
    print(result.derivative)  # → "nous"
    print(result.rationale)   # → "抽象度が高く..."
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mekhane.fep.derivative_selector import (
    select_derivative,
    DerivativeRecommendation,
    DERIVATIVE_DESCRIPTIONS,
    get_derivative_description,
)


@dataclass
class WorkflowResult:
    """Result of workflow execution with derivative selection."""
    theorem: str
    derivative: str
    confidence: float
    rationale: str
    alternatives: List[str]
    description: str
    processing_hints: Dict[str, str]


# Theorem to workflow mapping
THEOREM_TO_WORKFLOW: Dict[str, str] = {
    "O1": "/noe",
    "O2": "/bou",
    "O3": "/zet",
    "O4": "/ene",
    "S1": "/met",
    "S2": "/mek",
    "S3": "/sta",
    "S4": "/pra",
    "H1": "/pro",
    "H2": "/pis",
    "H3": "/ore",
    "H4": "/dox",
    "P1": "/kho",
    "P2": "/hod",
    "P3": "/tro",
    "P4": "/tek",
    "K1": "/euk",
    "K2": "/chr",
    "K3": "/tel",
    "K4": "/sop",
    "A1": "/pat",
    "A2": "/dia",
    "A3": "/gno",
    "A4": "/epi",
}


# Processing hints for each derivative
DERIVATIVE_PROCESSING_HINTS: Dict[str, Dict[str, str]] = {
    # O1 Noēsis
    "nous": {
        "phase1_focus": "普遍的前提の掘り出し",
        "phase2_focus": "原理的再構築",
        "output_style": "抽象的洞察・パターン認識",
    },
    "phro": {
        "phase1_focus": "文脈的前提の掘り出し",
        "phase2_focus": "実践的再構築",
        "output_style": "具体的判断・行動指針",
    },
    "meta": {
        "phase1_focus": "認知的前提の掘り出し",
        "phase2_focus": "信頼性再評価",
        "output_style": "確信度評価・Epochē判断",
    },
    # A2 Krisis
    "affi": {
        "decision_mode": "コミットメント志向",
        "output_style": "肯定的判定・採用理由",
    },
    "nega": {
        "decision_mode": "否定・拒否志向",
        "output_style": "否定的判定・却下理由",
    },
    "susp": {
        "decision_mode": "判断保留 (Epochē)",
        "output_style": "追加情報要求・不確実性明示",
    },
}


def run_workflow(theorem: str, problem_context: str) -> WorkflowResult:
    """
    Run a workflow with automatic derivative selection.
    
    Args:
        theorem: Theorem code (e.g., "O1", "A2")
        problem_context: User's problem description
    
    Returns:
        WorkflowResult with derivative selection and processing hints
    
    Example:
        >>> result = run_workflow("O1", "この問題の本質は何か")
        >>> result.derivative
        'nous'
    """
    # 1. Select derivative
    recommendation = select_derivative(theorem, problem_context)
    
    # 2. Get description
    description = get_derivative_description(theorem, recommendation.derivative)
    
    # 3. Get processing hints
    processing_hints = DERIVATIVE_PROCESSING_HINTS.get(
        recommendation.derivative, 
        {"note": "デフォルト処理"}
    )
    
    return WorkflowResult(
        theorem=theorem,
        derivative=recommendation.derivative,
        confidence=recommendation.confidence,
        rationale=recommendation.rationale,
        alternatives=recommendation.alternatives,
        description=description,
        processing_hints=processing_hints,
    )


def format_derivative_selection(result: WorkflowResult) -> str:
    """Format derivative selection result for display."""
    workflow = THEOREM_TO_WORKFLOW.get(result.theorem, "unknown")
    
    output = f"""
┌─[{result.theorem} 派生選択]────────────────────────────┐
│ ワークフロー: {workflow}
│ 推奨派生: {result.derivative}
│ 確信度: {result.confidence:.0%}
│ 理由: {result.rationale}
│ 代替: {', '.join(result.alternatives)}
├────────────────────────────────────────────────────────┤
│ 説明: {result.description}
└────────────────────────────────────────────────────────┘
"""
    
    if result.processing_hints:
        output += "\n処理ヒント:\n"
        for key, value in result.processing_hints.items():
            output += f"  • {key}: {value}\n"
    
    return output


def get_workflow_for_theorem(theorem: str) -> Optional[str]:
    """Get workflow path for a theorem."""
    return THEOREM_TO_WORKFLOW.get(theorem)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hegemonikón Workflow Runner")
    parser.add_argument("theorem", help="Theorem code (e.g., O1, A2)")
    parser.add_argument("problem", help="Problem context")
    
    args = parser.parse_args()
    
    result = run_workflow(args.theorem, args.problem)
    print(format_derivative_selection(result))
