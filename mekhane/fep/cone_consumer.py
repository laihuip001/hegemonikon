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
# ConeAdvice
# =============================================================================


@dataclass
class ConeAdvice:
    """Next-action recommendation from a Cone analysis.

    This is what makes the Cone a "consumer" type —
    structured data drives structured decisions.

    When action='devil', devil_detail is auto-populated with
    a DevilAttack containing structured contradiction analysis (CR-3).
    """

    action: str  # "proceed" | "investigate" | "devil" | "reweight"
    reason: str  # Human-readable justification
    suggested_wf: str = ""  # Recommended WF (e.g. "/dia devil")
    next_steps: List[str] = field(default_factory=list)
    urgency: float = 0.0  # 0.0 (低) - 1.0 (高)
    devil_detail: Optional[DevilAttack] = None  # CR-3: auto-populated

    def __repr__(self) -> str:
        wf = f" → {self.suggested_wf}" if self.suggested_wf else ""
        devil = f", devil={self.devil_detail}" if self.devil_detail else ""
        return f"ConeAdvice({self.action}{wf}, urgency={self.urgency:.1f}{devil})"


# =============================================================================
# advise() — Active inference decision
# =============================================================================


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

    CognitiveType-aware:
    - Understanding (O/H/K): V reflects interpretive diversity, tolerate more
    - Reasoning (S/P): V reflects logical contradiction, strict
    - Bridge (A): V at U/R boundary is naturally higher, lenient threshold

    Args:
        cone: A fully populated Cone from converge()

    Returns:
        ConeAdvice with action, reason, and suggested workflow
    """
    series_name = cone.series.name

    # --- Rule 1: Serious contradiction (V > 0.3) ---
    if cone.needs_devil:
        attack = devil_attack(cone)  # CR-3: auto-execute
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
        )

    # --- Rule 2: S-series strategy risk (V > 0.2) ---
    if cone.series == Series.S and cone.dispersion > 0.2:
        attack = devil_attack(cone)  # CR-3: auto-execute
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
        )

    # --- Rule 2.5: A-series Bridge tolerance ---
    # A-series spans U/R boundary, naturally higher V is expected
    if cone.series == Series.A and cone.dispersion > 0.25:
        # Determine dominant cognitive types in projections
        bridge_projs = [p.theorem_id for p in cone.projections
                        if p.theorem_id in COGNITIVE_TYPES
                        and COGNITIVE_TYPES[p.theorem_id] in (
                            CognitiveType.BRIDGE_U_TO_R,
                            CognitiveType.BRIDGE_R_TO_U,
                        )]
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
        )

    # --- Rule 3: Low confidence + moderate dispersion ---
    # CR-4: A-series excluded (already handled by Rule 2.5)
    if cone.dispersion > 0.1 and cone.confidence < 50 and cone.series != Series.A:
        # Choose WF based on series
        if cone.series == Series.K:
            wf = "/sop"  # K: 調査で解消
        else:
            wf = "/zet"  # O/S/H/P: 問いを深める
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
        )

    # --- Rule 4: PW bias check ---
    if (cone.resolution_method == "pw_weighted"
            and not is_uniform_pw(cone.pw)):
        # Check for extreme PW values
        extreme_keys = [k for k, v in cone.pw.items() if abs(v) > 0.7]
        if extreme_keys:
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
            )

    # --- Rule 5: Universal — proceed ---
    if cone.is_universal:
        return ConeAdvice(
            action="proceed",
            reason=f"V={cone.dispersion:.2f}, conf={cone.confidence:.0f}%: "
                   f"Limit 到達。統合判断を実行に移せる",
            next_steps=[
                "apex をアクション計画に変換",
            ],
            urgency=0.0,
        )

    # --- Default: moderate confidence, proceed ---
    return ConeAdvice(
        action="proceed",
        reason=f"V={cone.dispersion:.2f}, conf={cone.confidence:.0f}%: "
               f"概ね整合。実行可能",
        urgency=0.1,
    )


# =============================================================================
# Attractor-Cone Integration
# =============================================================================


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

