# PROOF: [L2/FEP] <- mekhane/fep/
# PURPOSE: Cone 構造データを消費し、次のアクションを推奨する
"""
Cone Consumer — Active Inference の実装

converge() が生成した Cone を消費し、次の WF/アクションを推奨する。
これは Hegemonikón の FEP サイクルにおける active inference:
予測誤差 (dispersion) を最小化するために次の行動を選択する。

Usage:
    from mekhane.fep.cone_consumer import advise
    cone = converge(series, outputs)
    advice = advise(cone)
    print(advice)  # → ConeAdvice(action="devil", ...)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import TYPE_CHECKING, List, Optional

from mekhane.fep.category import COGNITIVE_TYPES, Cone, CognitiveType, Series
from mekhane.fep.cone_builder import is_uniform_pw


# Pre-compiled regexes for devil_attack (CR-5: moved out of loop)
_NEG_RE = re.compile(
    r"(?:ない|しない|できない|不可|否定|反対|拒否"
    r"|stop|no|not|never|don'?t|won'?t|reject|cancel)",
    re.IGNORECASE,
)
_DIR_GO_RE = re.compile(
    r"(?:する|進む|開始|GO|yes|accept|approve|keep|continue|実行|追加)",
    re.IGNORECASE,
)
_DIR_WAIT_RE = re.compile(
    r"(?:しない|止める|中止|WAIT|no|reject|cancel|stop|remove|削除|廃止)",
    re.IGNORECASE,
)


# =============================================================================
# DevilAttack — Cocone 反例生成
# =============================================================================


# PURPOSE: A pair of projections that contradict each other
@dataclass
class ContradictionPair:
    """A pair of projections that contradict each other."""

    theorem_a: str  # e.g. "O1"
    theorem_b: str  # e.g. "O4"
    similarity: float  # Text similarity (lower = more contradictory)
    output_a: str
    output_b: str
    diagnosis: str = ""  # Human-readable explanation

    def __repr__(self) -> str:
        return f"Contradiction({self.theorem_a}↔{self.theorem_b}, sim={self.similarity:.2f})"


# PURPOSE: Result of a devil's advocate attack on a Cone
@dataclass
class DevilAttack:
    """Result of a devil's advocate attack on a Cone.

    圏論的解釈: Devil = Cocone
    Cone は全射を統合 (收束) するが、Cocone はその逆 — 全射を展開して矛盾を顕在化する。
    FEP 的解釈: Surprise を最大化する反例を生成し、予測誤差を意識させる。
    """

    cone: Cone
    contradictions: List[ContradictionPair]
    attack_summary: str  # 1-line summary of the attack
    counterarguments: List[str]  # Specific counterarguments
    resolution_paths: List[str]  # Suggested ways to resolve
    severity: float = 0.0  # 0.0 (mild) - 1.0 (severe)

    # PURPOSE: The most contradictory pair
    @property
    def worst_pair(self) -> Optional[ContradictionPair]:
        """The most contradictory pair."""
        if not self.contradictions:
            return None
        return min(self.contradictions, key=lambda c: c.similarity)

    def __repr__(self) -> str:
        return (
            f"DevilAttack(V={self.cone.dispersion:.2f}, "
            f"severity={self.severity:.1f}, "
            f"contradictions={len(self.contradictions)})"
        )


# PURPOSE: Generate a devil's advocate attack on a Cone
def devil_attack(cone: Cone) -> DevilAttack:
    """Generate a devil's advocate attack on a Cone.

    Cocone 構成: Cone の projections を対にして矛盾を検出し、
    反例 (counterargument) を構造的に生成する。

    This is BS-1 (theory-implementation gap) direct resolution:
    needs_devil property → actual devil_attack function.

    Strategy:
        1. Enumerate all projection pairs (C(4,2) = 6 pairs)
        2. Compute pairwise text similarity
        3. Identify contradiction signals (negation, direction)
        4. Generate counterarguments for low-similarity pairs
        5. Suggest resolution paths based on series type

    Args:
        cone: A Cone from converge()

    Returns:
        DevilAttack with structured adversarial analysis
    """
    projs = {p.theorem_id: p.output for p in cone.projections if p.output}

    # Step 1: Enumerate all pairs and compute similarity
    contradictions: List[ContradictionPair] = []
    ids = list(projs.keys())

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a_id, b_id = ids[i], ids[j]
            a_out, b_out = projs[a_id], projs[b_id]

            sim = SequenceMatcher(None, a_out, b_out).ratio()

            # Negation contradiction check (CR-5: uses module-level regex)
            a_neg = bool(_NEG_RE.search(a_out))
            b_neg = bool(_NEG_RE.search(b_out))
            neg_contradiction = (a_neg != b_neg) and (a_neg or b_neg)

            # Direction contradiction check (CR-5: uses module-level regex)
            a_go = bool(_DIR_GO_RE.search(a_out))
            a_wait = bool(_DIR_WAIT_RE.search(a_out))
            b_go = bool(_DIR_GO_RE.search(b_out))
            b_wait = bool(_DIR_WAIT_RE.search(b_out))
            dir_contradiction = (
                (a_go and not a_wait and b_wait and not b_go)
                or (b_go and not b_wait and a_wait and not a_go)
            )

            # Effective similarity (lower if contradictions found)
            effective_sim = sim
            if neg_contradiction:
                effective_sim *= 0.5
            if dir_contradiction:
                effective_sim *= 0.5

            # Build diagnosis
            diag_parts = []
            if neg_contradiction:
                diag_parts.append("否定語の不一致")
            if dir_contradiction:
                diag_parts.append("方向性の矛盾 (GO vs WAIT)")
            if sim < 0.3:
                diag_parts.append("テキスト類似度が極めて低い")

            pair = ContradictionPair(
                theorem_a=a_id,
                theorem_b=b_id,
                similarity=effective_sim,
                output_a=a_out[:100],
                output_b=b_out[:100],
                diagnosis="; ".join(diag_parts) if diag_parts else "微弱な不一致",
            )
            contradictions.append(pair)

    # Step 2: Sort by contradiction severity (lowest similarity first)
    contradictions.sort(key=lambda c: c.similarity)

    # Step 3: Generate counterarguments from worst contradictions
    counterarguments: List[str] = []
    for pair in contradictions[:3]:  # Top 3 worst
        if pair.similarity < 0.5:
            counterarguments.append(
                f"{pair.theorem_a} は「{pair.output_a[:40]}」、"
                f"一方 {pair.theorem_b} は「{pair.output_b[:40]}」"
                f"— {pair.diagnosis}"
            )

    if not counterarguments:
        counterarguments.append("明確な矛盾は検出されず、dispersion は分布の偏りに起因する")

    # Step 4: Resolution paths based on series
    series_name = cone.series.name
    resolution_paths: List[str] = []

    if cone.series == Series.S:
        resolution_paths = [
            f"/{series_name.lower()} を全定理で再実行し、前提を統一する",
            "/dia devil → S1(尺度) と S3(基準) の不整合を特定",
            "PW で低信頼の定理を抑制し、高信頼定理で再融合",
        ]
    elif cone.series == Series.O:
        resolution_paths = [
            "/noe+ → O1(認識) を深化して前提を再検証",
            "/zet → O3(探求) で矛盾の根本原因を問う",
            "PW で最も確信の高い定理に重み付けし再融合",
        ]
    elif cone.series == Series.A:
        resolution_paths = [
            "/dia epo → 判断停止で U/R 境界の矛盾を受容",
            "/epi → A4(知識) で確信度を引き上げる追加調査",
            "分解統治: 矛盾する定理を独立に再評価",
        ]
    else:
        resolution_paths = [
            f"/{series_name.lower()} を再実行し、矛盾する projection を修正",
            "/dia devil → 矛盾点を精査",
            "PW 調整で矛盾解消を試みる",
        ]

    # Step 5: Compute severity
    if contradictions:
        worst_sim = contradictions[0].similarity
        severity = min(1.0, max(0.0, 1.0 - worst_sim))
    else:
        severity = 0.0

    # Step 6: Attack summary
    n_serious = sum(1 for c in contradictions if c.similarity < 0.3)
    attack_summary = (
        f"V={cone.dispersion:.2f}: "
        f"{n_serious}/{len(contradictions)} 対に深刻な矛盾"
        if n_serious > 0
        else f"V={cone.dispersion:.2f}: 軽微な不整合のみ"
    )

    return DevilAttack(
        cone=cone,
        contradictions=contradictions,
        attack_summary=attack_summary,
        counterarguments=counterarguments,
        resolution_paths=resolution_paths,
        severity=severity,
    )


# =============================================================================
# Explanation Stack — Layer 2: Decision Trace
# =============================================================================


# PURPOSE: Record of a single rule evaluation in advise()
@dataclass
class RuleEvaluation:
    """Record of a single rule evaluation in advise().

    Each if-elif branch in advise() generates one RuleEvaluation.
    Together they form the trace — the "thinking path" of the decision.
    """

    rule_id: str        # "Rule 1: Contradiction (V > 0.3)"
    matched: bool       # Did this rule fire?
    reason: str         # "V=0.35 > 0.3" or "V=0.08 ≤ 0.3"
    series_specific: bool = False  # Is this a Series-specific rule?

    def __repr__(self) -> str:
        mark = "✓" if self.matched else "✗"
        return f"{mark} {self.rule_id}: {self.reason}"


# PURPOSE: An action that advise() considered but rejected
@dataclass
class RejectedAction:
    """An action that advise() considered but rejected.

    Layer 3: Justification — "why NOT this action?"
    Derived automatically from RuleEvaluation trace.
    """

    action: str         # "proceed", "investigate", "devil", "reweight"
    rule_id: str        # Which rule's non-match implies this rejection
    reason: str         # "V=0.35 > 0.3, devil takes priority"

    def __repr__(self) -> str:
        return f"✗ {self.action}: {self.reason}"


# PURPOSE: Complete reasoning trace of an advise() call
@dataclass
class DecisionTrace:
    """Complete reasoning trace of an advise() call.

    Layer 2 (Trace) + Layer 3 (Justification) combined.
    Built as a byproduct of advise()'s rule evaluation.

    The trace records EVERY rule checked, not just the one that matched.
    This is the "doctor showing the X-ray" — the process, not just the result.
    """

    evaluations: List[RuleEvaluation]
    rejected: List[RejectedAction] = field(default_factory=list)
    matched_rule: str = ""  # Final rule that fired

    def __repr__(self) -> str:
        n_eval = len(self.evaluations)
        n_rej = len(self.rejected)
        return f"Trace({n_eval} rules, {n_rej} rejected → {self.matched_rule})"


# =============================================================================
# Explanation Stack — Layer 1: ConeAdvice (Structure)
# =============================================================================


# PURPOSE: Next-action recommendation from a Cone analysis
@dataclass
class ConeAdvice:
    """Next-action recommendation from a Cone analysis.

    Explanation Stack:
      Layer 1: action, reason, urgency (Structure)
      Layer 2: trace (DecisionTrace — which rules were checked)
      Layer 3: trace.rejected (RejectedAction[] — why not other actions)
      Layer 4: format_advice_for_llm() (Narrative — see below)

    When action='devil', devil_detail is auto-populated with
    a DevilAttack containing structured contradiction analysis (CR-3).
    """

    action: str  # "proceed" | "investigate" | "devil" | "reweight"
    reason: str  # Human-readable justification
    suggested_wf: str = ""  # Recommended WF (e.g. "/dia devil")
    next_steps: List[str] = field(default_factory=list)
    urgency: float = 0.0  # 0.0 (低) - 1.0 (高)
    devil_detail: Optional[DevilAttack] = None  # CR-3: auto-populated
    trace: Optional[DecisionTrace] = None  # ES: Layer 2+3

    def __repr__(self) -> str:
        wf = f" → {self.suggested_wf}" if self.suggested_wf else ""
        devil = f", devil={self.devil_detail}" if self.devil_detail else ""
        trace = f", trace={self.trace}" if self.trace else ""
        return f"ConeAdvice({self.action}{wf}, urgency={self.urgency:.1f}{devil}{trace})"


# =============================================================================
# advise() — Active inference decision (with Explanation Stack)
# =============================================================================


# PURPOSE: Derive rejected actions from rule evaluations
def _derive_rejected(evaluations: List[RuleEvaluation]) -> List[RejectedAction]:
    """Derive Layer 3 (RejectedAction) from Layer 2 (RuleEvaluation).

    Each non-matched rule implies a rejected action.
    The action name is inferred from the rule's intended outcome.
    """
    # Rule → action mapping (what each rule would have produced)
    _RULE_ACTION_MAP = {
        "Rule 1": "devil",
        "Rule 2": "devil",
        "Rule 2.5": "investigate",
        "Rule 3": "investigate",
        "Rule 4": "reweight",
        "Rule 5": "proceed",
    }

    rejected = []
    for ev in evaluations:
        if not ev.matched:
            # Extract rule number prefix for action mapping
            rule_prefix = ev.rule_id.split(":")[0].strip()
            action = _RULE_ACTION_MAP.get(rule_prefix, "unknown")
            rejected.append(RejectedAction(
                action=action,
                rule_id=ev.rule_id,
                reason=ev.reason,
            ))
    return rejected


# PURPOSE: Consume a Cone and recommend the next action
def advise(cone: Cone) -> ConeAdvice:
    """Consume a Cone and recommend the next action.

    Decision table (priority order — first match wins):

    | Condition                          | Action      | WF           |
    |:-----------------------------------|:------------|:-------------|
    | V > 0.3 (needs_devil)              | devil       | /dia devil   |
    | S-series + V > 0.2                 | devil       | /dia devil   |
    | A-series (Bridge) + V > 0.25       | investigate | /dia epo     |
    | V > 0.1 + conf < 50               | investigate | /zet or /sop |
    | PW non-uniform + resolution=pw_w.  | reweight    | /dia epo     |
    | is_universal (V≤0.1, conf≥70)      | proceed     | —            |
    | else (low dispersion, moderate)    | proceed     | —            |

    Explanation Stack (Layer 2+3):
    Every rule check is recorded in DecisionTrace. Non-matched rules
    generate RejectedAction entries. The trace is attached to the
    returned ConeAdvice for inspection by LLM or developer.

    Args:
        cone: A fully populated Cone from converge()

    Returns:
        ConeAdvice with action, reason, suggested workflow, and trace
    """
    series_name = cone.series.name
    evals: List[RuleEvaluation] = []

    # --- Rule 1: Serious contradiction (V > 0.3) ---
    r1_match = cone.needs_devil
    evals.append(RuleEvaluation(
        rule_id="Rule 1: Contradiction (V > 0.3)",
        matched=r1_match,
        reason=f"V={cone.dispersion:.2f} {'>' if r1_match else '≤'} 0.3",
    ))
    if r1_match:
        attack = devil_attack(cone)
        trace = DecisionTrace(
            evaluations=evals,
            rejected=_derive_rejected(evals),
            matched_rule="Rule 1",
        )
        return ConeAdvice(
            action="devil",
            reason=f"V={cone.dispersion:.2f} > 0.3: 定理間に重大な矛盾。"
                   f" 解消法={cone.resolution_method}",
            suggested_wf="/dia devil",
            next_steps=[
                "矛盾する projection を特定",
                f"/{series_name.lower()} を再実行し、矛盾の原因を探る",
                "apex が projection と整合するか検証",
            ],
            urgency=min(1.0, cone.dispersion),
            devil_detail=attack,
            trace=trace,
        )

    # --- Rule 2: S-series strategy risk (V > 0.2) ---
    r2_match = cone.series == Series.S and cone.dispersion > 0.2
    r2_reason = (
        f"series={series_name}, V={cone.dispersion:.2f}"
        f" {'(S + V>0.2)' if r2_match else '(not S-series or V≤0.2)'}"
    )
    evals.append(RuleEvaluation(
        rule_id="Rule 2: S-series strategy (V > 0.2)",
        matched=r2_match,
        reason=r2_reason,
        series_specific=True,
    ))
    if r2_match:
        attack = devil_attack(cone)
        trace = DecisionTrace(
            evaluations=evals,
            rejected=_derive_rejected(evals),
            matched_rule="Rule 2",
        )
        return ConeAdvice(
            action="devil",
            reason=f"S-series (Reasoning) + V={cone.dispersion:.2f} > 0.2: "
                   f"戦略判断の矛盾は実行リスクが高い",
            suggested_wf="/dia devil",
            next_steps=[
                "S1(尺度) と S3(基準) の矛盾を確認",
                "S2(方法) が S4(実践) と整合するか検証",
            ],
            urgency=0.8,
            devil_detail=attack,
            trace=trace,
        )

    # --- Rule 2.5: A-series Bridge tolerance ---
    r25_match = cone.series == Series.A and cone.dispersion > 0.25
    r25_reason = (
        f"series={series_name}, V={cone.dispersion:.2f}"
        f" {'(A + V>0.25)' if r25_match else '(not A-series or V≤0.25)'}"
    )
    evals.append(RuleEvaluation(
        rule_id="Rule 2.5: A-series Bridge (V > 0.25)",
        matched=r25_match,
        reason=r25_reason,
        series_specific=True,
    ))
    if r25_match:
        bridge_projs = [p.theorem_id for p in cone.projections
                        if p.theorem_id in COGNITIVE_TYPES
                        and COGNITIVE_TYPES[p.theorem_id] in (
                            CognitiveType.BRIDGE_U_TO_R,
                            CognitiveType.BRIDGE_R_TO_U,
                        )]
        trace = DecisionTrace(
            evaluations=evals,
            rejected=_derive_rejected(evals),
            matched_rule="Rule 2.5",
        )
        return ConeAdvice(
            action="investigate",
            reason=f"A-series (Bridge U↔R) + V={cone.dispersion:.2f}: "
                   f"U/R 境界での矛盾は自然だが確認が必要。"
                   f" Bridge theorems: {bridge_projs}",
            suggested_wf="/dia epo",
            next_steps=[
                "A1(U→R) と A3(R→U) の方向が逆転していないか確認",
                "A2(Krisis) と A4(Epistēmē) の Reasoning 整合性を検証",
            ],
            urgency=0.5,
            trace=trace,
        )

    # --- Rule 3: Low confidence + moderate dispersion ---
    # CR-4: A-series excluded (already handled by Rule 2.5)
    r3_match = (cone.dispersion > 0.1 and cone.confidence < 50
                and cone.series != Series.A)
    r3_reason = (
        f"V={cone.dispersion:.2f}, conf={cone.confidence:.0f}%, "
        f"series={series_name}"
        f" {'(V>0.1, conf<50, not A)' if r3_match else '(conditions not met)'}"
    )
    evals.append(RuleEvaluation(
        rule_id="Rule 3: Low confidence (V > 0.1, conf < 50)",
        matched=r3_match,
        reason=r3_reason,
    ))
    if r3_match:
        if cone.series == Series.K:
            wf = "/sop"
        else:
            wf = "/zet"
        trace = DecisionTrace(
            evaluations=evals,
            rejected=_derive_rejected(evals),
            matched_rule="Rule 3",
        )
        return ConeAdvice(
            action="investigate",
            reason=f"V={cone.dispersion:.2f}, conf={cone.confidence:.0f}%: "
                   f"確信が不十分、追加調査が必要",
            suggested_wf=wf,
            next_steps=[
                f"conf を 70% 以上に引き上げる追加情報を収集",
                f"V を 0.1 以下にするために矛盾点を解消",
            ],
            urgency=0.5,
            trace=trace,
        )

    # --- Rule 4: PW bias check ---
    has_pw = (cone.resolution_method == "pw_weighted"
              and not is_uniform_pw(cone.pw))
    extreme_keys = []
    if has_pw:
        extreme_keys = [k for k, v in cone.pw.items() if abs(v) > 0.7]
    r4_match = has_pw and bool(extreme_keys)
    r4_reason = (
        f"resolution={cone.resolution_method}, "
        f"extreme_pw={extreme_keys if extreme_keys else 'none'}"
    )
    evals.append(RuleEvaluation(
        rule_id="Rule 4: PW bias (extreme weights)",
        matched=r4_match,
        reason=r4_reason,
    ))
    if r4_match:
        trace = DecisionTrace(
            evaluations=evals,
            rejected=_derive_rejected(evals),
            matched_rule="Rule 4",
        )
        return ConeAdvice(
            action="reweight",
            reason=f"PW バイアスが強い: {', '.join(extreme_keys)}。"
                   f" 判断停止で検証を推奨",
            suggested_wf="/dia epo",
            next_steps=[
                f"極端な PW ({extreme_keys}) の根拠を確認",
                "PW なし (uniform) で再実行し結果を比較",
            ],
            urgency=0.4,
            trace=trace,
        )

    # --- Rule 5: Universal — proceed ---
    r5_match = cone.is_universal
    evals.append(RuleEvaluation(
        rule_id="Rule 5: Universal (V≤0.1, conf≥70)",
        matched=r5_match,
        reason=f"is_universal={cone.is_universal}",
    ))
    if r5_match:
        trace = DecisionTrace(
            evaluations=evals,
            rejected=_derive_rejected(evals),
            matched_rule="Rule 5",
        )
        return ConeAdvice(
            action="proceed",
            reason=f"V={cone.dispersion:.2f}, conf={cone.confidence:.0f}%: "
                   f"Limit 到達。統合判断を実行に移せる",
            next_steps=[
                "apex をアクション計画に変換",
            ],
            urgency=0.0,
            trace=trace,
        )

    # --- Default: moderate confidence, proceed ---
    evals.append(RuleEvaluation(
        rule_id="Default: proceed",
        matched=True,
        reason=f"V={cone.dispersion:.2f}, conf={cone.confidence:.0f}%: no prior rule matched",
    ))
    trace = DecisionTrace(
        evaluations=evals,
        rejected=_derive_rejected(evals),
        matched_rule="Default",
    )
    return ConeAdvice(
        action="proceed",
        reason=f"V={cone.dispersion:.2f}, conf={cone.confidence:.0f}%: "
               f"概ね整合。実行可能",
        urgency=0.1,
        trace=trace,
    )


# =============================================================================
# Attractor-Cone Integration
# =============================================================================


# PURPOSE: Enriched advise() that incorporates Attractor diagnosis
def advise_with_attractor(
    cone: Cone,
    oscillation: str,
    attractor_confidence: float,
    attractor_series: Optional[str] = None,
) -> ConeAdvice:
    """Enriched advise() that incorporates Attractor diagnosis.

    This bridges the two FEP subsystems:
    - Attractor: "which Series should we use?" (macro-level routing)
    - Cone: "does the Series output cohere?" (micro-level validation)

    Integration rules (applied as post-processing on base advise):

    | Oscillation | Effect on ConeAdvice                        |
    |:------------|:--------------------------------------------|
    | CLEAR       | No change — Attractor is confident           |
    | POSITIVE    | devil → investigate if urgency < 0.8         |
    | NEGATIVE    | urgency += 0.2 — weak convergence is risky   |
    | WEAK        | proceed → investigate                        |

    Series mismatch (attractor says O, cone says S) → investigate.

    Args:
        cone: A Cone from converge()
        oscillation: OscillationType.value string ("clear"/"positive"/"negative"/"weak")
        attractor_confidence: Attractor's top_similarity (0.0-1.0)
        attractor_series: Primary Series from Attractor (e.g. "O")

    Returns:
        ConeAdvice, potentially modified by Attractor context
    """
    # Start with base advise
    base = advise(cone)

    # --- Series mismatch check ---
    if (attractor_series
            and attractor_series != cone.series.name
            and base.action == "proceed"):
        return ConeAdvice(
            action="investigate",
            reason=f"Series 不一致: Attractor={attractor_series}, "
                   f"Cone={cone.series.name}。routing を再検討",
            suggested_wf="/zet",
            next_steps=[
                f"Attractor が {attractor_series} を推薦した理由を確認",
                f"入力を {cone.series.name}-series として再評価",
            ],
            urgency=0.6,
            devil_detail=base.devil_detail,
        )

    # --- Oscillation modifiers ---
    if oscillation == "negative":
        # Attractor の収束が弱い → urgency を上げる
        return ConeAdvice(
            action=base.action,
            reason=f"{base.reason} | Attractor: NEGATIVE "
                   f"(conf={attractor_confidence:.2f}) — 収束弱",
            suggested_wf=base.suggested_wf,
            next_steps=base.next_steps + [
                "Attractor Basin 未分化を解消するために入力を具体化",
            ],
            urgency=min(1.0, base.urgency + 0.2),
            devil_detail=base.devil_detail,
        )

    if oscillation == "weak":
        # 引力圏外 → investigate に昇格
        if base.action == "proceed":
            return ConeAdvice(
                action="investigate",
                reason=f"{base.reason} | Attractor: WEAK — "
                       f"引力圏外のため追加調査推奨",
                suggested_wf="/zet",
                next_steps=[
                    "入力テキストを再構成して Attractor 収束を試みる",
                    "Series を手動指定して再実行",
                ],
                urgency=0.5,
                devil_detail=base.devil_detail,
            )

    if oscillation == "positive":
        # 多面的 — V が高くても自然
        if base.action == "devil" and base.urgency < 0.8:
            return ConeAdvice(
                action="investigate",
                reason=f"{base.reason} | Attractor: POSITIVE — "
                       f"multi-Series 共鳴のため V 高は自然",
                suggested_wf=base.suggested_wf or "/dia epo",
                next_steps=base.next_steps + [
                    "multi-Series の交差点を /x で分析",
                ],
                urgency=max(0.3, base.urgency - 0.2),
                devil_detail=base.devil_detail,
            )

    # CLEAR or no modification needed
    return base


# =============================================================================
# Explanation Stack — Layer 4: Narrative (format_for_llm)
# =============================================================================


# PURPOSE: Convert ConeAdvice to LLM system prompt injection text
def format_advice_for_llm(advice: ConeAdvice) -> str:
    """Convert ConeAdvice to LLM system prompt injection text.

    Explanation Stack Layer 4 — the "narrative layer".
    Symmetric with attractor_advisor.format_for_llm().

    Output format (3 sections):
      [Cone: <action> | V=<dispersion> | <reason_summary>]
      [Trace: Rule1✗ → Rule2✓ ...]
      [Rejected: proceed(reason), investigate(reason)]

    This text is injected into the LLM's context so it can generate
    a natural language narrative for the Creator.

    Args:
        advice: A ConeAdvice from advise() or advise_with_attractor()

    Returns:
        Formatted string for LLM injection
    """
    lines = []

    # --- Section 1: Cone summary ---
    wf = f" → {advice.suggested_wf}" if advice.suggested_wf else ""
    devil = ""
    if advice.devil_detail:
        d = advice.devil_detail
        worst = d.worst_pair
        worst_desc = (
            f", worst={worst.theorem_a}↔{worst.theorem_b}"
            if worst else ""
        )
        devil = f", severity={d.severity:.2f}{worst_desc}"
    lines.append(
        f"[Cone: {advice.action}{wf} | "
        f"urgency={advice.urgency:.1f}{devil}]"
    )

    # --- Section 2: Trace ---
    if advice.trace:
        trace_parts = []
        for ev in advice.trace.evaluations:
            mark = "✓" if ev.matched else "✗"
            # Short rule name (e.g. "R1" from "Rule 1: ...")
            short = ev.rule_id.split(":")[0].replace("Rule ", "R")
            trace_parts.append(f"{short}{mark}")
        lines.append(f"[Trace: {' → '.join(trace_parts)}]")

    # --- Section 3: Rejected ---
    if advice.trace and advice.trace.rejected:
        rej_parts = []
        for r in advice.trace.rejected:
            # Compact: "proceed(V>0.3)"
            short_reason = r.reason.split(",")[0] if r.reason else "—"
            rej_parts.append(f"{r.action}({short_reason})")
        lines.append(f"[Rejected: {', '.join(rej_parts)}]")

    # --- Next steps ---
    if advice.next_steps:
        lines.append(f"[Next: {'; '.join(advice.next_steps)}]")

    return "\n".join(lines)
