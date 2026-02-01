# PROOF: [L1/定理] CCL→実行基盤が必要
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
from mekhane.fep.encoding import get_x_series_recommendations


@dataclass
class XSeriesRecommendation:
    """X-series next step recommendation."""

    x_id: str
    target: str
    workflow: str
    reason: str


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
    x_series_recommendations: List[XSeriesRecommendation]


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

# Workflow directory (absolute path)
WORKFLOWS_DIR = "/home/laihuip001/oikos/.agent/workflows"


def get_workflow_path(theorem_or_workflow: str) -> Optional[str]:
    """
    Get the absolute file path to a workflow .md file.

    Args:
        theorem_or_workflow: Either theorem code (e.g., "O1") or workflow name (e.g., "/noe" or "noe")

    Returns:
        Absolute path to the workflow .md file, or None if not found

    Example:
        >>> get_workflow_path("O1")
        '/home/laihuip001/oikos/.agent/workflows/noe.md'
        >>> get_workflow_path("/noe")
        '/home/laihuip001/oikos/.agent/workflows/noe.md'
        >>> get_workflow_path("noe")
        '/home/laihuip001/oikos/.agent/workflows/noe.md'
    """
    # Normalize input
    input_str = theorem_or_workflow.upper()

    # Check if it's a theorem code
    if input_str in THEOREM_TO_WORKFLOW:
        workflow = THEOREM_TO_WORKFLOW[input_str]
    else:
        # Assume it's a workflow name
        workflow = theorem_or_workflow.lower().lstrip("/")

    # Remove leading slash if present
    workflow_name = workflow.lstrip("/")

    # Construct path
    workflow_path = os.path.join(WORKFLOWS_DIR, f"{workflow_name}.md")

    if os.path.exists(workflow_path):
        return workflow_path
    return None


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


# =============================================================================
# X-series: 36 関係 (定理間接続)
# =============================================================================

X_SERIES_RELATIONS: Dict[str, Dict[str, List[str]]] = {
    # O-series からの接続 (X-O)
    "O1": {"O": ["O3"], "S": ["S1"], "H": ["H1"], "A": ["A2"]},
    "O2": {"K": ["K3"], "O": ["O4"]},
    "O3": {"O": ["O1"], "A": ["A4"]},
    "O4": {"P": ["P4"], "S": ["S4"], "H": ["H2"]},
    # S-series からの接続 (X-S)
    "S1": {"S": ["S4"], "P": ["P1"], "K": ["K2"]},
    "S2": {"S": ["S4"], "P": ["P4"]},
    "S3": {"K": ["K3"], "A": ["A2"]},
    "S4": {"O": ["O4"], "H": ["H4"]},
    # H-series からの接続 (X-H)
    "H1": {"H": ["H2"], "O": ["O1"]},
    "H2": {"O": ["O4"], "H": ["H4"]},
    "H3": {"P": ["P1"], "H": ["H4"]},
    "H4": {"S": ["S4"], "K": ["K4"], "A": ["A3"]},
    # P-series からの接続 (X-P)
    "P1": {"P": ["P2"], "H": ["H3"]},
    "P2": {"P": ["P3", "P4"]},
    "P3": {"K": ["K2"]},
    "P4": {"O": ["O4"], "S": ["S2"], "A": ["A4"]},
    # K-series からの接続 (X-K)
    "K1": {"H": ["H1"], "K": ["K3"]},
    "K2": {"S": ["S1"]},
    "K3": {"P": ["P3"], "O": ["O2"]},
    "K4": {"O": ["O1"], "A": ["A4"]},
    # A-series からの接続 (X-A)
    "A1": {"H": ["H1"]},
    "A2": {"K": ["K1"], "A": ["A4"]},
    "A3": {"S": ["S3"]},
    "A4": {"O": ["O1"], "P": ["P4"]},
}


def suggest_next_theorems(current_theorem: str) -> List[Dict[str, str]]:
    """
    X-series から次に推奨される定理を提案。

    Args:
        current_theorem: 現在の定理コード (e.g., "O1", "A2")

    Returns:
        List of {theorem, workflow, relation} dicts

    Example:
        >>> suggest_next_theorems("O1")
        [{'theorem': 'S1', 'workflow': '/met', 'relation': 'X-OS'},
         {'theorem': 'H1', 'workflow': '/pro', 'relation': 'X-OH'}, ...]
    """
    relations = X_SERIES_RELATIONS.get(current_theorem.upper(), {})
    suggestions = []

    current_series = current_theorem[0].upper()

    for target_series, theorems in relations.items():
        for theorem in theorems:
            workflow = THEOREM_TO_WORKFLOW.get(theorem, "unknown")
            relation_id = f"X-{current_series}{target_series}"
            suggestions.append(
                {
                    "theorem": theorem,
                    "workflow": workflow,
                    "relation": relation_id,
                }
            )

    return suggestions


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
        recommendation.derivative, {"note": "デフォルト処理"}
    )

    # 4. Get X-series recommendations
    series = theorem[0]  # Extract series letter (O, S, H, P, K, A)
    x_recs_raw = get_x_series_recommendations(series, recommendation.confidence)
    x_recs = [
        XSeriesRecommendation(
            x_id=r["x_id"],
            target=r["target"],
            workflow=r["workflow"],
            reason=r["reason"],
        )
        for r in x_recs_raw
    ]

    return WorkflowResult(
        theorem=theorem,
        derivative=recommendation.derivative,
        confidence=recommendation.confidence,
        rationale=recommendation.rationale,
        alternatives=recommendation.alternatives,
        description=description,
        processing_hints=processing_hints,
        x_series_recommendations=x_recs,
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

    # X-series next step recommendations
    if result.x_series_recommendations:
        output += "\n⏭️ X-series 推奨次ステップ:\n"
        for rec in result.x_series_recommendations:
            output += f"  → {rec.workflow} ({rec.x_id}: {rec.reason})\n"

    return output


def get_workflow_for_theorem(theorem: str) -> Optional[str]:
    """Get workflow path for a theorem."""
    return THEOREM_TO_WORKFLOW.get(theorem)


# CLI interface
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Hegemonikón Workflow Runner")
    parser.add_argument(
        "theorem", help="Theorem code (e.g., O1, A2) or workflow name (e.g., noe)"
    )
    parser.add_argument("problem", nargs="?", default="", help="Problem context")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed diagnostics"
    )
    parser.add_argument(
        "--show-path", action="store_true", help="Show workflow file path only"
    )
    parser.add_argument(
        "--execute", action="store_true", help="Output JSON for agent execution"
    )

    args = parser.parse_args()

    # --show-path mode: just return the workflow path
    if args.show_path:
        path = get_workflow_path(args.theorem)
        if path:
            print(path)
        else:
            print(f"Error: Workflow not found for '{args.theorem}'", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    # For derivative selection, we need a problem context
    if not args.problem and not args.show_path:
        print(
            "Error: problem context is required unless --show-path is used",
            file=sys.stderr,
        )
        sys.exit(1)

    result = run_workflow(args.theorem, args.problem)
    workflow_path = get_workflow_path(args.theorem)

    # --execute mode: output JSON for agent consumption
    if args.execute:
        output = {
            "theorem": result.theorem,
            "workflow": THEOREM_TO_WORKFLOW.get(result.theorem, "unknown"),
            "workflow_path": workflow_path,
            "derivative": result.derivative,
            "confidence": result.confidence,
            "rationale": result.rationale,
            "alternatives": result.alternatives,
            "description": result.description,
            "processing_hints": result.processing_hints,
            "x_series_next": [
                {
                    "id": r.x_id,
                    "target": r.target,
                    "workflow": r.workflow,
                    "reason": r.reason,
                }
                for r in result.x_series_recommendations
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        sys.exit(0)

    if args.verbose:
        print("=== 診断モード ===", flush=True)
        print(f'入力: theorem={args.theorem}, problem="{args.problem[:50]}..."')
        print(f"ワークフローパス: {workflow_path}")
        print()
        print("[派生選択詳細]")
        print(f"  選択: {result.derivative}")
        print(f"  信頼度: {result.confidence:.0%}")
        print(f"  代替: {', '.join(result.alternatives)}")
        print(f"  理由: {result.rationale}")
        print()
        print("[X-series 接続]")
        next_steps = suggest_next_theorems(args.theorem)
        for s in next_steps:
            print(f"  → {s['workflow']} ({s['relation']}: {s['theorem']})")
        print()

    print(format_derivative_selection(result), flush=True)
