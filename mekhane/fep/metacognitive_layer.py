# PROOF: [L2/FEP] <- mekhane/fep/
# PURPOSE: 全WFに適用される普遍的メタ認知チェック
"""
PROOF: [L2/FEP] このファイルは存在しなければならない

A0 → MP研究 (arXiv:2308.05342) により、メタ認知の5段階が
     LLM の推論品質を有意に改善することが示された
   → Hegemonikón の全WFに普遍的メタ認知チェックを適用する必要がある
   → UML (Universal Metacognitive Layer) として実装する
   → metacognitive_layer.py が担う

Q.E.D.

---

Universal Metacognitive Layer (UML)

MP の5段階を全WFの前後に環境強制するレイヤー。

Pre-check (WF実行前):
  Stage 1 (O1): 入力を正しく理解したか？
  Stage 2 (A1): 第一印象・直感はどうか？

Post-check (WF実行後):
  Stage 3 (A2): 出力を批判的に再評価したか？
  Stage 4 (O4): 決定は妥当か？ 説明できるか？
  Stage 5 (A4): 確信度は適切か？ 過信していないか？

Feedback loop (AMP: Adaptive Metacognitive Prompting):
  Stage 3 で過信検出 → Stage 1 に戻る (X-AO1 射)

Source: Wang & Zhao (2023) "Metacognitive Prompting Improves
        Understanding in Large Language Models" arXiv:2308.05342

Usage:
    from mekhane.fep.metacognitive_layer import run_full_uml, UMLReport

    report = run_full_uml(
        context="ユーザーの入力テキスト",
        output="WFが生成した出力テキスト",
        wf_name="noe",
        confidence=85.0,
    )
    print(report.summary)
    if report.feedback_loop_triggered:
        print("⚠️ AMP feedback: Stage 3 → Stage 1 再理解が必要")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from mekhane.fep.category import COGNITIVE_TYPES, CognitiveType


# =============================================================================
# Constants
# =============================================================================

# MP False Positive rate: 32.5% of "high confidence" answers are wrong
# Source: arXiv:2308.05342 Table 2
MP_FALSE_POSITIVE_RATE = 0.325

# Confidence threshold above which overconfidence warning is triggered
OVERCONFIDENCE_THRESHOLD = 90.0

# Minimum output length to consider "substantive"
MIN_SUBSTANTIVE_LENGTH = 20

# Maximum number of AMP feedback loops before force-proceeding
MAX_FEEDBACK_LOOPS = 3


# =============================================================================
# Enums & Data Classes
# =============================================================================


class UMLStage(Enum):
    """The 5 stages of UML, mapped to MP stages and HGK theorems."""

    PRE_UNDERSTANDING = "pre_understanding"  # MP S1 → O1 Noēsis
    PRE_INTUITION = "pre_intuition"          # MP S2 → A1 Pathos
    POST_EVALUATION = "post_evaluation"      # MP S3 → A2 Krisis
    POST_DECISION = "post_decision"          # MP S4 → O4 Energeia
    POST_CONFIDENCE = "post_confidence"      # MP S5 → A4 Epistēmē


# Stage → HGK theorem mapping (η components)
STAGE_TO_THEOREM: Dict[UMLStage, str] = {
    UMLStage.PRE_UNDERSTANDING: "O1",
    UMLStage.PRE_INTUITION: "A1",
    UMLStage.POST_EVALUATION: "A2",
    UMLStage.POST_DECISION: "O4",
    UMLStage.POST_CONFIDENCE: "A4",
}

# Stage → cognitive type (derived from COGNITIVE_TYPES)
STAGE_TO_COGNITIVE: Dict[UMLStage, CognitiveType] = {
    stage: COGNITIVE_TYPES[tid]
    for stage, tid in STAGE_TO_THEOREM.items()
}

# Stage → human-readable question (JP)
STAGE_QUESTIONS: Dict[UMLStage, str] = {
    UMLStage.PRE_UNDERSTANDING: "入力を正しく理解したか？ 要点を自分の言葉で言い換えられるか？",
    UMLStage.PRE_INTUITION: "第一印象はどうか？ 違和感・共感・疑問はあるか？",
    UMLStage.POST_EVALUATION: "出力を批判的に再評価したか？ 反例・盲点はないか？",
    UMLStage.POST_DECISION: "この決定は妥当か？ 別の人に説明できるか？",
    UMLStage.POST_CONFIDENCE: "確信度は適切か？ 過信していないか？ (FP 32.5% を忘れるな)",
}


@dataclass
class MetacognitiveCheck:
    """Single metacognitive check result."""

    stage: UMLStage
    question: str  # What was asked
    result: str  # Self-assessment answer
    passed: bool  # Whether the check passed
    confidence: float = 0.0  # Confidence in this check (0-100)
    theorem: str = ""  # Corresponding HGK theorem
    cognitive_type: str = ""  # Understanding / Reasoning / Bridge

    @property
    def stage_label(self) -> str:
        """Human-readable stage label."""
        labels = {
            UMLStage.PRE_UNDERSTANDING: "Pre-1 (O1: 理解)",
            UMLStage.PRE_INTUITION: "Pre-2 (A1: 直感)",
            UMLStage.POST_EVALUATION: "Post-1 (A2: 批判)",
            UMLStage.POST_DECISION: "Post-2 (O4: 決定)",
            UMLStage.POST_CONFIDENCE: "Post-3 (A4: 確信度)",
        }
        return labels.get(self.stage, self.stage.value)


@dataclass
class UMLReport:
    """Complete UML check report for a WF execution."""

    wf_name: str
    pre_checks: List[MetacognitiveCheck] = field(default_factory=list)
    post_checks: List[MetacognitiveCheck] = field(default_factory=list)
    feedback_loop_triggered: bool = False
    feedback_loop_count: int = 0
    feedback_reason: str = ""

    @property
    def all_checks(self) -> List[MetacognitiveCheck]:
        """All checks in execution order."""
        return self.pre_checks + self.post_checks

    @property
    def overall_pass(self) -> bool:
        """All checks passed."""
        return all(c.passed for c in self.all_checks)

    @property
    def pass_count(self) -> int:
        """Number of checks that passed."""
        return sum(1 for c in self.all_checks if c.passed)

    @property
    def total_count(self) -> int:
        """Total number of checks."""
        return len(self.all_checks)

    @property
    def summary(self) -> str:
        """One-line summary."""
        status = "✅ PASS" if self.overall_pass else "⚠️ FAIL"
        fb = f" [AMP ×{self.feedback_loop_count}]" if self.feedback_loop_triggered else ""
        return (
            f"UML [{self.wf_name}]: {status} "
            f"({self.pass_count}/{self.total_count}){fb}"
        )

    def describe(self) -> str:
        """Multi-line description for WF output."""
        lines = [
            f"### UML Report: /{self.wf_name}",
            "",
            "| Stage | Question | Pass | θ |",
            "|:------|:---------|:----:|:-:|",
        ]
        for check in self.all_checks:
            icon = "✅" if check.passed else "❌"
            conf = f"{check.confidence:.0f}%" if check.confidence > 0 else "—"
            lines.append(
                f"| {check.stage_label} | {check.question[:40]}… | {icon} | {conf} |"
            )

        lines.append("")
        lines.append(f"**Result**: {self.summary}")

        if self.feedback_loop_triggered:
            lines.append(
                f"\n> [!WARNING]\n"
                f"> **AMP Feedback Loop**: {self.feedback_reason}\n"
                f"> Loop count: {self.feedback_loop_count}/{MAX_FEEDBACK_LOOPS}"
            )

        return "\n".join(lines)


# =============================================================================
# Core Check Functions
# =============================================================================


# PURPOSE: Pre-check Stage 1 — 入力の理解確認 (O1 Noēsis 射)
def check_understanding(context: str) -> MetacognitiveCheck:
    """Pre-check Stage 1: Verify understanding of input.

    Maps to η₁: S1 → O1 (Understanding → Noēsis)

    Checks:
    - Input is non-empty
    - Input has sufficient substance (> MIN_SUBSTANTIVE_LENGTH)
    """
    stage = UMLStage.PRE_UNDERSTANDING
    question = STAGE_QUESTIONS[stage]

    # Check: is there meaningful input?
    has_substance = len(context.strip()) >= MIN_SUBSTANTIVE_LENGTH
    passed = has_substance

    result = (
        "入力は十分な長さがあり、理解可能" if passed
        else "入力が短すぎる、または空 — 理解を確認できない"
    )

    return MetacognitiveCheck(
        stage=stage,
        question=question,
        result=result,
        passed=passed,
        confidence=80.0 if passed else 30.0,
        theorem="O1",
        cognitive_type=CognitiveType.UNDERSTANDING.value,
    )


# PURPOSE: Pre-check Stage 2 — 直感的判断の確認 (A1 Pathos 射)
def check_intuition(context: str) -> MetacognitiveCheck:
    """Pre-check Stage 2: Register initial intuition / gut feeling.

    Maps to η₂: S2 → A1 (Preliminary Judgment → Pathos)

    This stage captures the pre-reflective assessment.
    In LLM terms: does the input trigger any known patterns?
    """
    stage = UMLStage.PRE_INTUITION
    question = STAGE_QUESTIONS[stage]

    # Check: can we form an initial impression?
    # Heuristic: if context contains question marks, uncertainty words, etc.
    has_question = "?" in context or "？" in context
    has_uncertainty = any(w in context for w in [
        "わからない", "不明", "uncertain", "maybe", "perhaps",
        "かもしれない", "推測", "仮説",
    ])

    # Initial impression is always formable (even "I don't know" is valid)
    passed = True
    result = "初期印象を形成: "
    if has_question:
        result += "明確な問いがある — 探求的文脈"
    elif has_uncertainty:
        result += "不確実性がある — 慎重さが必要"
    else:
        result += "明確な入力 — 標準処理"

    return MetacognitiveCheck(
        stage=stage,
        question=question,
        result=result,
        passed=passed,
        confidence=70.0,
        theorem="A1",
        cognitive_type=CognitiveType.BRIDGE_U_TO_R.value,
    )


# PURPOSE: Post-check Stage 3 — 批判的再評価 (A2 Krisis 射)
def check_evaluation(
    output: str,
    context: str,
    confidence: float = 0.0,
) -> MetacognitiveCheck:
    """Post-check Stage 3: Critical re-evaluation of output.

    Maps to η₃: S3 → A2 (Critical Evaluation → Krisis)

    Checks:
    - Output is non-empty and substantive
    - Output addresses the context (basic relevance)
    - No overconfidence detected (FP 32.5% threshold)
    """
    stage = UMLStage.POST_EVALUATION
    question = STAGE_QUESTIONS[stage]

    issues: List[str] = []

    # Check 1: Output is substantive
    if len(output.strip()) < MIN_SUBSTANTIVE_LENGTH:
        issues.append("出力が短すぎる")

    # Check 2: Overconfidence detection
    if confidence > OVERCONFIDENCE_THRESHOLD:
        issues.append(
            f"確信度 {confidence}% > {OVERCONFIDENCE_THRESHOLD}% — "
            f"FP {MP_FALSE_POSITIVE_RATE*100}% を考慮"
        )

    # Check 3: Basic output-context alignment (share any content?)
    if output and context:
        # Simple heuristic: at least some overlap in bigrams
        ctx_chars = set(context[:200])  # First 200 chars of context
        out_chars = set(output[:200])
        overlap = len(ctx_chars & out_chars)
        if overlap < 5:
            issues.append("出力が入力と関連性が低い可能性")

    passed = len(issues) == 0
    result = "批判的再評価 PASS" if passed else f"問題検出: {'; '.join(issues)}"

    return MetacognitiveCheck(
        stage=stage,
        question=question,
        result=result,
        passed=passed,
        confidence=min(confidence, 100.0 - MP_FALSE_POSITIVE_RATE * 100),
        theorem="A2",
        cognitive_type=CognitiveType.REASONING.value,
    )


# PURPOSE: Post-check Stage 4 — 決定の妥当性確認 (O4 Energeia 射)
def check_decision(output: str) -> MetacognitiveCheck:
    """Post-check Stage 4: Verify decision is sound and explainable.

    Maps to η₄: S4 → O4 (Decision + Explanation → Energeia)

    Checks:
    - Output exists (a decision was made)
    - Output is not just a copy of a template
    """
    stage = UMLStage.POST_DECISION
    question = STAGE_QUESTIONS[stage]

    has_output = len(output.strip()) >= MIN_SUBSTANTIVE_LENGTH

    # Check for template-like output (placeholder detection)
    template_markers = ["TODO", "FIXME", "placeholder", "(未設定)", "TBD"]
    has_template = any(m in output for m in template_markers)

    passed = has_output and not has_template
    if not has_output:
        result = "決定なし — 出力が空"
    elif has_template:
        result = "テンプレート/プレースホルダーが残存 — 決定が不完全"
    else:
        result = "決定は形式的に有効"

    return MetacognitiveCheck(
        stage=stage,
        question=question,
        result=result,
        passed=passed,
        confidence=75.0 if passed else 20.0,
        theorem="O4",
        cognitive_type=CognitiveType.UNDERSTANDING.value,
    )


# PURPOSE: Post-check Stage 5 — 確信度の適切性評価 (A4 Epistēmē 射)
def check_confidence(
    confidence: float = 0.0,
    output: str = "",
) -> MetacognitiveCheck:
    """Post-check Stage 5: Confidence calibration assessment.

    Maps to η₅: S5 → A4 (Confidence Assessment → Epistēmē)

    Checks:
    - Confidence is explicitly stated (not default 0)
    - No overconfidence (> 90% triggers warning)
    - No extreme underconfidence (< 10% triggers warning)

    Warning: FP rate of 32.5% means ~1/3 of high-confidence claims are wrong.
    """
    stage = UMLStage.POST_CONFIDENCE
    question = STAGE_QUESTIONS[stage]

    issues: List[str] = []

    # Check 1: Confidence is stated
    if confidence == 0.0:
        issues.append("確信度が未設定 (0%) — 明示せよ")

    # Check 2: Overconfidence
    if confidence > OVERCONFIDENCE_THRESHOLD:
        issues.append(
            f"確信度 {confidence}% — 過信リスク: "
            f"FP {MP_FALSE_POSITIVE_RATE*100:.1f}% を忘れるな"
        )

    # Check 3: Extreme underconfidence
    if 0 < confidence < 10:
        issues.append(
            f"確信度 {confidence}% — 極端に低い: "
            "本当にそこまで不確実か？"
        )

    # Check 4: Output contains confidence label?
    has_label = any(lbl in output for lbl in ["[確信]", "[推定]", "[仮説]"])

    passed = len(issues) == 0
    result = "確信度キャリブレーション OK" if passed else f"問題: {'; '.join(issues)}"
    if has_label:
        result += " [BC-6 ラベル検出]"

    return MetacognitiveCheck(
        stage=stage,
        question=question,
        result=result,
        passed=passed,
        confidence=confidence if confidence > 0 else 50.0,
        theorem="A4",
        cognitive_type=CognitiveType.REASONING.value,
    )


# =============================================================================
# Orchestrators
# =============================================================================


# PURPOSE: 全Pre-checkを一括実行
def run_pre_checks(context: str) -> List[MetacognitiveCheck]:
    """Run all pre-WF metacognitive checks (Stage 1-2).

    Call this BEFORE executing a workflow.

    Returns:
        List of 2 MetacognitiveChecks (understanding, intuition)
    """
    return [
        check_understanding(context),
        check_intuition(context),
    ]


# PURPOSE: 全Post-checkを一括実行
def run_post_checks(
    output: str,
    context: str = "",
    confidence: float = 0.0,
) -> List[MetacognitiveCheck]:
    """Run all post-WF metacognitive checks (Stage 3-5).

    Call this AFTER executing a workflow.

    Returns:
        List of 3 MetacognitiveChecks (evaluation, decision, confidence)
    """
    return [
        check_evaluation(output, context, confidence),
        check_decision(output),
        check_confidence(confidence, output),
    ]


# PURPOSE: 5段階すべてを一括実行 + AMP フィードバックループ
def run_full_uml(
    context: str,
    output: str,
    wf_name: str = "unknown",
    confidence: float = 0.0,
) -> UMLReport:
    """Run the complete Universal Metacognitive Layer.

    Executes all 5 stages and detects AMP feedback loop triggers.

    Feedback loop conditions (from mp_natural_transformation.md):
    - Stage 3 (A2) detects overconfidence → loop back to Stage 1 (O1)
    - Stage 5 (A4) confidence > 90% on complex task → re-evaluate

    Args:
        context: Input text that triggered the WF
        output: WF's output text
        wf_name: Name of the workflow (for reporting)
        confidence: Confidence score (0-100)

    Returns:
        UMLReport with all checks and feedback loop status
    """
    pre = run_pre_checks(context)
    post = run_post_checks(output, context, confidence)

    # AMP Feedback loop detection
    feedback_triggered = False
    feedback_count = 0
    feedback_reason = ""

    # Condition 1: Post-evaluation (A2) failed on overconfidence
    eval_check = post[0]  # Stage 3
    if not eval_check.passed and confidence > OVERCONFIDENCE_THRESHOLD:
        feedback_triggered = True
        feedback_count = 1
        feedback_reason = (
            f"A2 (Krisis) が過信を検出: confidence={confidence}% > "
            f"{OVERCONFIDENCE_THRESHOLD}%. X-AO1 射により O1 (Noēsis) へ戻る。"
            f" 「そもそも入力を正しく理解していたか？」を再確認せよ。"
        )

    # Condition 2: Confidence check (A4) triggers on high confidence
    conf_check = post[2]  # Stage 5
    if not conf_check.passed and confidence > OVERCONFIDENCE_THRESHOLD:
        feedback_triggered = True
        feedback_count = max(feedback_count, 1)
        if not feedback_reason:
            feedback_reason = (
                f"A4 (Epistēmē) が過信を検出: confidence={confidence}%. "
                f"FP {MP_FALSE_POSITIVE_RATE*100:.1f}% に基づく再評価が必要。"
            )

    return UMLReport(
        wf_name=wf_name,
        pre_checks=pre,
        post_checks=post,
        feedback_loop_triggered=feedback_triggered,
        feedback_loop_count=feedback_count,
        feedback_reason=feedback_reason,
    )
