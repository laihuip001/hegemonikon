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

⚠️ Phase 1 Status: SPECIFICATION (仕様書 / Contract)

  現在の実装は LLM のプロンプト注入によるメタ認知ではなく、
  テキストベースのヒューリスティック検査である。
  本来 MP が要求する「自己質問→応答→再評価」のループは
  Python 関数では実現できず、LLM プロンプトチェーンとして
  Phase 2 で実装する必要がある。

  Phase 1 (現在): ヒューリスティック検査 = CONTRACT
    - 各 Stage の検査条件を形式的に定義
    - BC-9 のリマインダーとして機能
    - 「常に PASS を返す Stage は Stage ではない」(/m dia+ E2)
  Phase 2 (将来): プロンプト注入による真の環境強制
    - sel_enforcement との統合
    - LLM に Stage 質問を強制的に回答させる仕組み

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


# PURPOSE: The 5 stages of UML, mapped to MP stages and HGK theorems
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


# PURPOSE: Single metacognitive check result
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

    # PURPOSE: Human-readable stage label
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


# PURPOSE: Complete UML check report for a WF execution
@dataclass
class UMLReport:
    """Complete UML check report for a WF execution."""

    wf_name: str
    pre_checks: List[MetacognitiveCheck] = field(default_factory=list)
    post_checks: List[MetacognitiveCheck] = field(default_factory=list)
    feedback_loop_triggered: bool = False
    feedback_loop_count: int = 0
    feedback_reason: str = ""

    # PURPOSE: All checks in execution order
    @property
    def all_checks(self) -> List[MetacognitiveCheck]:
        """All checks in execution order."""
        return self.pre_checks + self.post_checks

    # PURPOSE: All checks passed
    @property
    def overall_pass(self) -> bool:
        """All checks passed."""
        return all(c.passed for c in self.all_checks)

    # PURPOSE: Number of checks that passed
    @property
    def pass_count(self) -> int:
        """Number of checks that passed."""
        return sum(1 for c in self.all_checks if c.passed)

    # PURPOSE: Total number of checks
    @property
    def total_count(self) -> int:
        """Total number of checks."""
        return len(self.all_checks)

    # PURPOSE: One-line summary
    @property
    def summary(self) -> str:
        """One-line summary."""
        status = "✅ PASS" if self.overall_pass else "⚠️ FAIL"
        fb = f" [AMP ×{self.feedback_loop_count}]" if self.feedback_loop_triggered else ""
        return (
            f"UML [{self.wf_name}]: {status} "
            f"({self.pass_count}/{self.total_count}){fb}"
        )

    # PURPOSE: Multi-line description for WF output
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

    Fails when (/m dia+ P1 fix):
    - Input is too short to form intuition (< 10 chars)
    - Input contains contradictory signals (both urgent AND reflective)
    """
    stage = UMLStage.PRE_INTUITION
    question = STAGE_QUESTIONS[stage]

    issues: List[str] = []

    # Check 1: Sufficient substance to form an impression
    stripped = context.strip()
    if len(stripped) < 10:
        issues.append("入力が短すぎて直感を形成できない")

    # Check 2: Contradictory signals detection
    has_question = "?" in context or "？" in context
    has_uncertainty = any(w in context for w in [
        "わからない", "不明", "uncertain", "maybe", "perhaps",
        "かもしれない", "推測", "仮説",
    ])
    # Urgency: intentional request to hurry (C1 fix: exclude 急に/急すぎ)
    has_urgency = any(w in context for w in [
        "緊急", "urgent", "今すぐ", "至急", "immediately",
        "急いで", "急ぎで", "急を要する", "早急",
    ])
    # Reflection: intentional request to slow down (C1 fix: stem forms)
    has_reflection = any(w in context for w in [
        "じっくり", "熟考", "慎重", "carefully", "deliberate",
        "ゆっくり", "落ち着いて", "深く考え",
    ])

    # Contradiction: urgent + reflective = ambiguous intuition
    contradictory = has_urgency and has_reflection
    if contradictory:
        issues.append("矛盾する信号: 緊急性と熟考が同時に存在 — 直感が定まらない")

    passed = len(issues) == 0

    # Build result description
    if not passed:
        result = f"直感形成に問題: {'; '.join(issues)}"
        confidence = 30.0
    elif has_question:
        result = "初期印象を形成: 明確な問いがある — 探求的文脈"
        confidence = 70.0
    elif has_uncertainty:
        result = "初期印象を形成: 不確実性がある — 慎重さが必要"
        confidence = 60.0
    elif has_urgency:
        result = "初期印象を形成: 緊急性がある — 即応モード"
        confidence = 75.0
    else:
        result = "初期印象を形成: 明確な入力 — 標準処理"
        confidence = 70.0

    return MetacognitiveCheck(
        stage=stage,
        question=question,
        result=result,
        passed=passed,
        confidence=confidence,
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

    Executes all 5 stages and implements AMP feedback loop recursion.

    AMP (Adaptive Metacognitive Prompting) feedback loop (/m dia+ P3):
    - Stage 3 (A2) detects overconfidence → loop back to Stage 1 (O1)
    - Each loop reduces effective confidence by FP rate (32.5%)
    - Max loops: MAX_FEEDBACK_LOOPS (3)
    - If still failing after max loops, proceed with current understanding

    Args:
        context: Input text that triggered the WF
        output: WF's output text
        wf_name: Name of the workflow (for reporting)
        confidence: Confidence score (0-100)

    Returns:
        UMLReport with all checks and feedback loop status
    """
    feedback_count = 0
    feedback_reasons: List[str] = []
    effective_confidence = confidence

    # Store the final pre/post checks across loops
    final_pre: List[MetacognitiveCheck] = []
    final_post: List[MetacognitiveCheck] = []

    # C2 fix: Accumulated feedback enriches context for each loop.
    # This makes each iteration's pre-check meaningfully different,
    # approximating MP's "re-understanding" process.
    enriched_context = context

    for loop_idx in range(MAX_FEEDBACK_LOOPS + 1):
        pre = run_pre_checks(enriched_context)
        post = run_post_checks(output, enriched_context, effective_confidence)

        final_pre = pre
        final_post = post

        # Check AMP trigger conditions
        eval_check = post[0]  # Stage 3 (A2)
        conf_check = post[2]  # Stage 5 (A4)

        overconfidence_detected = (
            (not eval_check.passed and effective_confidence > OVERCONFIDENCE_THRESHOLD)
            or (not conf_check.passed and effective_confidence > OVERCONFIDENCE_THRESHOLD)
        )

        if not overconfidence_detected or loop_idx == MAX_FEEDBACK_LOOPS:
            # No overconfidence or max loops reached — stop
            break

        # AMP feedback: reduce confidence and re-evaluate
        feedback_count += 1

        # Collect failed post-check results as feedback
        failed_issues = [
            c.result for c in post if not c.passed
        ]
        feedback_summary = "; ".join(failed_issues)
        reason = (
            f"Loop {feedback_count}: confidence={effective_confidence:.1f}% > "
            f"{OVERCONFIDENCE_THRESHOLD}%. 検出問題: {feedback_summary}. "
            f"X-AO1 射で O1 に戻り再理解。"
        )
        feedback_reasons.append(reason)

        # Enrich context with feedback for next iteration's pre-check
        enriched_context = (
            f"{context}\n[AMP feedback loop {feedback_count}] "
            f"前回検出: {feedback_summary}"
        )

        # Reduce effective confidence by FP rate
        effective_confidence *= (1.0 - MP_FALSE_POSITIVE_RATE)

    feedback_triggered = feedback_count > 0
    feedback_reason = " → ".join(feedback_reasons) if feedback_reasons else ""

    return UMLReport(
        wf_name=wf_name,
        pre_checks=final_pre,
        post_checks=final_post,
        feedback_loop_triggered=feedback_triggered,
        feedback_loop_count=feedback_count,
        feedback_reason=feedback_reason,
    )


# =============================================================================
# Phase 2: Prompt Injection
# =============================================================================


# PURPOSE: WF turbo ブロックに注入するメタ認知プロンプトを生成
def generate_prompt_injection(
    wf_name: str,
    stage: UMLStage,
    context: str = "",
) -> str:
    """指定 Stage のメタ認知プロンプトを生成。

    Phase 2: LLM の turbo ブロックに注入し、
    MP 5段階を「環境で強制」する。

    Args:
        wf_name: ワークフロー名
        stage: UML Stage
        context: 入力コンテキスト（オプション）

    Returns:
        WF turbo ブロックに注入する質問文字列
    """
    theorem = STAGE_TO_THEOREM.get(stage, "?")
    question = STAGE_QUESTIONS.get(stage, "")
    ctype = STAGE_TO_COGNITIVE.get(stage)
    type_label = ctype.name if ctype else ""

    # Pre-check stages: "Before you begin..."
    if stage in (UMLStage.PRE_UNDERSTANDING, UMLStage.PRE_INTUITION):
        prefix = "【UML Pre-check】"
        instruction = "以下の質問に1-2文で回答してから、本題に進んでください。"
    else:
        prefix = "【UML Post-check】"
        instruction = "出力を確定する前に、以下の質問に回答してください。"

    lines = [
        f"{prefix} Stage {theorem} ({type_label})",
        f"WF: /{wf_name}",
        f"",
        f"❓ {question}",
        f"",
        f"{instruction}",
    ]

    if context and stage == UMLStage.PRE_UNDERSTANDING:
        lines.append(f"")
        lines.append(f"入力の要約: 「{context[:100]}{'...' if len(context) > 100 else ''}」")

    return "\n".join(lines)


# PURPOSE: 全 Pre-check プロンプトを一括生成
def generate_pre_injection(wf_name: str, context: str = "") -> str:
    """WF 実行前に注入する全 Pre-check プロンプトを生成。"""
    parts = [
        generate_prompt_injection(wf_name, UMLStage.PRE_UNDERSTANDING, context),
        "",
        generate_prompt_injection(wf_name, UMLStage.PRE_INTUITION, context),
    ]
    return "\n".join(parts)


# PURPOSE: 全 Post-check プロンプトを一括生成
def generate_post_injection(wf_name: str) -> str:
    """WF 実行後に注入する全 Post-check プロンプトを生成。"""
    parts = [
        generate_prompt_injection(wf_name, UMLStage.POST_EVALUATION),
        "",
        generate_prompt_injection(wf_name, UMLStage.POST_DECISION),
        "",
        generate_prompt_injection(wf_name, UMLStage.POST_CONFIDENCE),
    ]
    return "\n".join(parts)
