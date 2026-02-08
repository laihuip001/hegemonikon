# PROOF: [L2/ユーティリティ] <- mekhane/fep/
"""
PROOF: [L2/ユーティリティ] このファイルは存在しなければならない

A0 → Hub Peras WF (@converge) で Cone を計算する必要がある
   → V[outputs] (分散度) を自動計算し、解消法を提案する
   → C0: Precision Weighting で各定理の重みを動的に決定する
   → cone_builder.py が担う

Q.E.D.

---

Cone Builder — Hub Peras @converge C0-C3 支援ユーティリティ

Hub WF (/o, /s, /h, /p, /k, /a) の @converge C0-C3 を支援する。
C0: PW 決定 → C1: Cone 構築 + V[outputs] → C2: PW 加重融合 → C3: 普遍性検証

Usage:
    from mekhane.fep.cone_builder import converge

    result = converge(
        series=Series.O,
        outputs={"O1": "深い認識", "O2": "強い意志", "O3": "鋭い問い", "O4": "確実な行動"},
        pw={"O1": 1.0, "O3": 0.5},  # O1 を最重視、O3 やや重視
    )
    print(result.apex)               # 統合判断
    print(result.dispersion)         # V[outputs]
    print(result.resolution_method)  # simple/pw_weighted/root
    print(result.pw)                 # {'O1': 1.0, 'O3': 0.5}
    print(result.pw_weights)         # 正規化済み重み
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, List, Optional

from mekhane.fep.category import (
    COGNITIVE_TYPES,
    FUNCTORS,
    MORPHISMS,
    NATURAL_TRANSFORMATIONS,
    Cone,
    CognitiveType,
    Functor,
    Morphism,
    NaturalTransformation,
    Series,
    build_cone,
)


# 否定語パターン (日本語 + 英語)
_NEGATION_RE = re.compile(
    r"(?:ない|しない|できない|不可|否定|反対|拒否|中止"
    r"|stop|no|not|never|don'?t|won'?t|reject|cancel)",
    re.IGNORECASE,
)
# 方向性: GO 系
_DIR_GO = re.compile(
    r"(?:する|進む|開始|GO|yes|accept|approve|keep|continue|実行|追加)",
    re.IGNORECASE,
)
# 方向性: WAIT 系
_DIR_WAIT = re.compile(
    r"(?:しない|止める|中止|WAIT|no|reject|cancel|stop|remove|削除|廃止)",
    re.IGNORECASE,
)


def _char_bigrams(text: str) -> List[str]:
    """Generate character bigrams from text (whitespace removed).

    Used for Jaccard similarity — captures topic overlap even in Japanese
    where SequenceMatcher's character-level matching performs poorly.
    """
    clean = re.sub(r"\s+", "", text)
    return [clean[i:i + 2] for i in range(len(clean) - 1)]


# =============================================================================
# C0: Precision Weighting (PW)
# =============================================================================


# PURPOSE: C0 — PW の正規化。raw pw [-1, +1] → 融合用重み [0, 2]
def normalize_pw(
    outputs: Dict[str, str],
    pw: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """Normalize Precision Weighting for fusion.

    Formula: weight_i = 1 + pw_i
    - pw_i = 0  → weight = 1.0 (neutral, uniform)
    - pw_i = +1 → weight = 2.0 (double emphasis)
    - pw_i = -1 → weight = 0.0 (fully suppressed)

    Returns:
        Dict[str, float]: normalized weights (0.0 - 2.0)
    """
    if pw is None:
        pw = {}

    return {
        tid: 1.0 + max(-1.0, min(1.0, pw.get(tid, 0.0)))
        for tid in outputs
    }


# PURPOSE: PW が均等かどうか判定する
def is_uniform_pw(pw: Optional[Dict[str, float]]) -> bool:
    """Check if precision weighting is uniform (all zero or not specified)."""
    if not pw:
        return True
    return all(abs(v) < 1e-9 for v in pw.values())


# =============================================================================
# C1: 射の対比 (Contrast) — V[outputs]
# =============================================================================


# PURPOSE: @converge C1 — 射の対比 (Contrast): V[outputs] を計算する
def compute_dispersion(outputs: Dict[str, str]) -> float:
    """Compute V[outputs] — the dispersion of theorem outputs.

    Uses pairwise text similarity + negation detection + direction coding
    to estimate how much the 4 outputs agree or contradict.

    Components:
        1. Ensemble similarity (SequenceMatcher + bigram Jaccard) → base dispersion
        2. Negation contradiction → bonus (テキスト間で否定が混在)
        3. Direction contradiction → bonus (GO vs WAIT が混在)

    The ensemble approach addresses BS-2 (Japanese short text V being
    systematically high). SequenceMatcher works at character level,
    which is poor for Japanese. Bigram Jaccard captures topic overlap
    via shared character pairs — higher for texts about the same topic.

    Returns:
        float: dispersion score (0.0-1.0)
        0.0 = all outputs identical
        1.0 = all outputs completely different
    """
    if not outputs or len(outputs) <= 1:
        return 0.0

    values = list(outputs.values())
    similarities: List[float] = []

    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            # Method 1: SequenceMatcher (character-level)
            seq_ratio = SequenceMatcher(None, values[i], values[j]).ratio()

            # Method 2: Bigram Jaccard (topic-level, better for Japanese)
            bigrams_a = set(_char_bigrams(values[i]))
            bigrams_b = set(_char_bigrams(values[j]))
            if bigrams_a or bigrams_b:
                jaccard = len(bigrams_a & bigrams_b) / len(bigrams_a | bigrams_b)
            else:
                jaccard = 1.0

            # Ensemble: take the max — if either method sees similarity,
            # the texts are not contradictory
            similarities.append(max(seq_ratio, jaccard))

    if not similarities:
        return 0.0

    avg_similarity = sum(similarities) / len(similarities)
    base = 1.0 - avg_similarity

    # 否定矛盾ボーナス: 一部だけ否定語がある = 矛盾
    neg_flags = [bool(_NEGATION_RE.search(v)) for v in values]
    neg_bonus = 0.0
    if any(neg_flags) and not all(neg_flags):
        neg_bonus = 0.15  # 否定の混在で +0.15

    # 方向性矛盾ボーナス: GO と WAIT が混在
    dir_bonus = 0.0
    dirs = []
    for v in values:
        go = bool(_DIR_GO.search(v))
        wait = bool(_DIR_WAIT.search(v))
        if go and not wait:
            dirs.append(1)
        elif wait and not go:
            dirs.append(-1)
        else:
            dirs.append(0)
    non_zero = [d for d in dirs if d != 0]
    if non_zero and any(d > 0 for d in non_zero) and any(d < 0 for d in non_zero):
        dir_bonus = 0.2  # 方向性矛盾で +0.2

    return round(min(1.0, base + neg_bonus + dir_bonus), 3)


# =============================================================================
# C2: Cone の頂点探索 (Resolve) — PW 加重融合
# =============================================================================


# PURPOSE: @converge C2 — 解消法を判定する (PW 考慮)
def resolve_method(
    dispersion: float,
    pw: Optional[Dict[str, float]] = None,
) -> str:
    """Determine resolution method based on V[outputs] + PW.

    | V[outputs] | PW     | Method         |
    |:-----------|:-------|:---------------|
    | > 0.3      | any    | root           |
    | > 0.1      | any    | pw_weighted    |
    | ≤ 0.1      | ≠ 0    | pw_weighted    |
    | ≤ 0.1      | = 0    | simple         |

    Returns:
        str: "simple", "pw_weighted", or "root"
    """
    if dispersion > 0.3:
        return "root"
    elif dispersion > 0.1:
        return "pw_weighted"
    elif not is_uniform_pw(pw):
        return "pw_weighted"
    else:
        return "simple"


# PURPOSE: PW 加重融合テーブルを計算する
def compute_pw_table(
    outputs: Dict[str, str],
    pw: Optional[Dict[str, float]] = None,
) -> List[Dict]:
    """Compute the PW weighting table for each theorem.

    Returns a list of dicts with:
    - theorem_id: str
    - output: str (truncated)
    - pw_raw: float (-1 to +1)
    - weight: float (0 to 2, normalized)
    - weight_pct: float (percentage contribution)
    """
    weights = normalize_pw(outputs, pw)
    total = sum(weights.values())
    if total == 0:
        total = 1.0  # avoid division by zero

    table = []
    for tid, output in outputs.items():
        raw = (pw or {}).get(tid, 0.0)
        w = weights[tid]
        table.append({
            "theorem_id": tid,
            "output": output[:50] + "..." if len(output) > 50 else output,
            "pw_raw": raw,
            "weight": w,
            "weight_pct": round(w / total * 100, 1),
        })
    return table


# =============================================================================
# Main: converge() — C0-C3 一括実行
# =============================================================================


# PURPOSE: @converge C0-C3 を一括実行する
def converge(
    series: Series,
    outputs: Dict[str, str],
    pw: Optional[Dict[str, float]] = None,
    apex: Optional[str] = None,
    confidence: float = 0.0,
    context: Optional[str] = None,
    agent: object = None,
) -> Cone:
    """Execute @converge C0-C3 and return a fully populated Cone.

    This is the main entry point for Hub Peras workflows.

    Args:
        series: Which series (O/S/H/P/K/A)
        outputs: Dict mapping theorem_id -> output string
        pw: Precision Weighting dict {theorem_id: weight}.
            weight ∈ [-1, +1]. 0 = neutral, +1 = emphasize, -1 = suppress.
            None or empty = uses pw_adapter cascade to auto-resolve.
        apex: Optional pre-computed integrated judgment
        confidence: Optional confidence score (0-100)
        context: Optional natural language context for PW inference
        agent: Optional HegemonikónFEPAgent for PW derivation

    Returns:
        Cone with C0 pw, C1 projections, C2 resolution, C3 universality

    Formula (C2 weighted fusion):
        統合出力 = Σ(定理_i × (1 + pw_i)) / Σ(1 + pw_i)
    """
    # C0: Precision Weighting (pw_adapter cascade)
    if pw is not None:
        cone_pw = pw
    else:
        try:
            from mekhane.fep.pw_adapter import resolve_pw
            cone_pw = resolve_pw(
                series.name,
                context=context,
                agent=agent,
            )
        except ImportError:
            cone_pw = {}

    # C1: Build Cone with projections
    cone = build_cone(series, outputs)
    cone.pw = {k: max(-1.0, min(1.0, v)) for k, v in cone_pw.items()}

    # C1: Compute dispersion
    cone.dispersion = compute_dispersion(outputs)

    # C2: Determine resolution method (PW-aware)
    cone.resolution_method = resolve_method(cone.dispersion, cone_pw)

    # C2: Set apex if provided
    if apex:
        cone.apex = apex

    # C3: Cone 品質評価 (自動計算)
    if confidence > 0:
        cone.confidence = confidence  # 外部指定を優先
    else:
        # 自動計算: base = (1 - dispersion) * 100
        base_conf = (1.0 - cone.dispersion) * 100.0
        # 否定ペナルティ: apex と projection の矛盾
        penalty = 0.0
        if cone.apex:
            apex_neg = bool(_NEGATION_RE.search(cone.apex))
            for proj in cone.projections:
                if proj.output and bool(_NEGATION_RE.search(proj.output)) != apex_neg:
                    penalty += 5.0
        cone.confidence = max(0.0, min(100.0, base_conf - penalty))

    cone.is_universal = cone.dispersion <= 0.1 and cone.confidence >= 70.0

    return cone


# =============================================================================
# Display
# =============================================================================


# PURPOSE: 全 Series の圏論的位置を表示するユーティリティ
def describe_cone(cone: Cone) -> str:
    """Format a Cone as human-readable text for WF output."""
    has_pw = not is_uniform_pw(cone.pw)

    # Header
    lines = [
        f"## Cone: {cone.series.value}-series",
        "",
    ]

    # C0: PW section (if non-uniform)
    if has_pw:
        lines.extend([
            "### C0: Precision Weighting",
            "",
        ])
        table = compute_pw_table(
            {p.theorem_id: p.output for p in cone.projections},
            cone.pw,
        )
        lines.append("| Theorem | pw | Weight | % |")
        lines.append("|:--------|:--:|:------:|:--:|")
        for row in table:
            pw_str = f"+{row['pw_raw']}" if row["pw_raw"] > 0 else str(row["pw_raw"])
            lines.append(
                f"| {row['theorem_id']} | {pw_str} | {row['weight']:.1f} | {row['weight_pct']}% |"
            )
        lines.append("")

    # C1: Projections
    lines.extend([
        "### C1: 射の対比",
        "",
        "| Theorem | Hom Label | Output |",
        "|:--------|:----------|:-------|",
    ])
    for proj in cone.projections:
        lines.append(f"| {proj.theorem_id} | {proj.hom_label} | {proj.output} |")

    # C2: Resolution
    lines.extend([
        "",
        f"**V[outputs]** = {cone.dispersion:.3f}"
        + (" ✅" if cone.dispersion <= 0.1
           else " ⚠️" if cone.dispersion <= 0.3
           else " 🔴"),
        f"**Resolution** = {cone.resolution_method}",
        f"**Apex** = {cone.apex or '(未設定)'}",
    ])

    # C3: Cone 品質評価
    lines.extend([
        f"**Confidence** = {cone.confidence:.0f}%",
        f"**Universal** = {'✅ Yes' if cone.is_universal else '❌ No'}",
    ])
    if cone.series == Series.S and cone.dispersion > 0.1:
        lines.append("⚠️ **Devil's Advocate 推奨** (S-series, V > 0.1)")

    return "\n".join(lines)


# =============================================================================
# Natural Transformation Verification
# =============================================================================


@dataclass
class NaturalityResult:
    """Result of verifying the naturality condition for a natural transformation.

    Naturality condition: G(f) ∘ α_X = α_Y ∘ F(f)
    For each morphism f: X → Y in the source category.
    """

    transformation_name: str
    is_natural: bool  # All checks passed
    checks: List[Dict]  # Individual check results
    violations: List[str]  # Human-readable violation descriptions

    @property
    def summary(self) -> str:
        """One-line summary."""
        n_pass = sum(1 for c in self.checks if c["pass"])
        return (
            f"{self.transformation_name}: "
            f"{n_pass}/{len(self.checks)} checks passed"
            + ("" if self.is_natural else f" — {len(self.violations)} violations")
        )


# PURPOSE: Verify naturality condition for a natural transformation
def verify_naturality(
    nt: NaturalTransformation,
    source_functor: Optional[Functor] = None,
    target_functor: Optional[Functor] = None,
) -> NaturalityResult:
    """Verify the naturality condition: G(f) ∘ α_X = α_Y ∘ F(f).

    For each morphism f: X → Y in the source functor's morphism_map,
    checks that the naturality square commutes:

        F(X) --α_X--> G(X)
         |              |
       F(f)           G(f)
         |              |
         v              v
        F(Y) --α_Y--> G(Y)

    Args:
        nt: The natural transformation α: F ⇒ G
        source_functor: F (auto-resolved from FUNCTORS if not given)
        target_functor: G (auto-resolved from FUNCTORS if not given)

    Returns:
        NaturalityResult with per-morphism check details
    """
    # Auto-resolve functors
    if source_functor is None:
        source_functor = FUNCTORS.get(nt.source_functor.lower())
    if target_functor is None:
        target_functor = FUNCTORS.get(nt.target_functor.lower())

    checks: List[Dict] = []
    violations: List[str] = []

    # If we can't resolve both functors, check component consistency only
    if source_functor is None or target_functor is None:
        # Fallback: verify that all components map to valid theorems
        for src_obj, tgt_obj in nt.components.items():
            is_valid = tgt_obj in COGNITIVE_TYPES
            check = {
                "source_obj": src_obj,
                "target_obj": tgt_obj,
                "type": "component_validity",
                "pass": is_valid,
            }
            checks.append(check)
            if not is_valid:
                violations.append(
                    f"Component α_{src_obj} = {tgt_obj}: "
                    f"target {tgt_obj} is not a valid theorem"
                )
        return NaturalityResult(
            transformation_name=nt.name,
            is_natural=len(violations) == 0,
            checks=checks,
            violations=violations,
        )

    # Full naturality check: for each morphism in source functor
    for mor_id, mapped_mor_id in source_functor.morphism_map.items():
        # Parse source morphism X → Y
        parts = mor_id.replace("→", "->").split("->")
        if len(parts) != 2:
            # Not a parseable morphism, skip
            continue

        src_x, src_y = parts[0].strip(), parts[1].strip()

        # α_X: component at X
        alpha_x = nt.component_at(src_x)
        # α_Y: component at Y
        alpha_y = nt.component_at(src_y)

        # F(f): how the source functor maps the morphism
        f_of_f = mapped_mor_id

        # G(f): how the target functor maps the same morphism
        # (if target_functor has a morphism_map)
        g_of_f = (
            target_functor.morphism_map.get(mor_id)
            if target_functor
            else None
        )

        # Check: both components must exist
        if alpha_x is None or alpha_y is None:
            check = {
                "morphism": mor_id,
                "source_obj": src_x,
                "target_obj": src_y,
                "alpha_x": alpha_x,
                "alpha_y": alpha_y,
                "type": "component_missing",
                "pass": False,
            }
            checks.append(check)
            missing = src_x if alpha_x is None else src_y
            violations.append(
                f"Morphism {mor_id}: component α_{missing} is undefined"
            )
            continue

        # Structural commutativity check:
        # G(f) ∘ α_X and α_Y ∘ F(f) should arrive at the same target theorem
        # In our registry, α maps source objects to HGK theorems.
        # The naturality square commutes if:
        #   mapping(α_X) through the HGK morphism structure = α_Y
        #
        # Operational check: does a morphism path exist from α_X to α_Y
        # in the MORPHISMS registry?
        path_exists = any(
            m.source == alpha_x and m.target == alpha_y
            for m in MORPHISMS.values()
        )

        check = {
            "morphism": mor_id,
            "source_obj": src_x,
            "target_obj": src_y,
            "alpha_x": alpha_x,
            "alpha_y": alpha_y,
            "f_of_f": f_of_f,
            "g_of_f": g_of_f,
            "path_exists": path_exists,
            "type": "naturality_square",
            "pass": path_exists,
        }
        checks.append(check)

        if not path_exists:
            violations.append(
                f"Morphism {mor_id}: no path from α_{src_x}={alpha_x} "
                f"to α_{src_y}={alpha_y} in MORPHISMS. "
                f"Naturality square may not commute."
            )

    return NaturalityResult(
        transformation_name=nt.name,
        is_natural=len(violations) == 0,
        checks=checks,
        violations=violations,
    )


# PURPOSE: Classify a theorem's cognitive type (Understanding/Reasoning/Bridge)
def classify_cognitive_type(theorem_id: str) -> CognitiveType:
    """Look up the cognitive type for a theorem.

    Args:
        theorem_id: e.g. "O1", "A1", "K4"

    Returns:
        CognitiveType enum value

    Raises:
        KeyError: if theorem_id is not in the registry
    """
    return COGNITIVE_TYPES[theorem_id]


# PURPOSE: Check if a morphism crosses the Understanding/Reasoning boundary
def is_cross_boundary_morphism(
    source_id: str, target_id: str
) -> Optional[str]:
    """Determine if a morphism crosses the U/R boundary.

    Returns:
        "U→R" if source is Understanding and target is Reasoning
        "R→U" if source is Reasoning and target is Understanding
        None if both are same type or if either is Bridge/Mixed
    """
    src_type = COGNITIVE_TYPES.get(source_id)
    tgt_type = COGNITIVE_TYPES.get(target_id)

    if src_type is None or tgt_type is None:
        return None

    u_types = {CognitiveType.UNDERSTANDING, CognitiveType.BRIDGE_U_TO_R}
    r_types = {CognitiveType.REASONING, CognitiveType.BRIDGE_R_TO_U}

    if src_type in u_types and tgt_type in r_types:
        return "U→R"
    elif src_type in r_types and tgt_type in u_types:
        return "R→U"
    return None


# =============================================================================
# CLI Entry Point — @converge turbo blocks call this
# =============================================================================


def _parse_pw(pw_str: str) -> Dict[str, float]:
    """Parse PW string: 'O1:0.5,O3:-0.5' → {'O1': 0.5, 'O3': -0.5}

    Invalid values are silently skipped (defensive parsing).
    """
    if not pw_str:
        return {}
    result = {}
    for pair in pw_str.split(","):
        pair = pair.strip()
        if ":" in pair:
            k, v = pair.split(":", 1)
            try:
                result[k.strip()] = float(v.strip())
            except ValueError:
                pass  # Skip invalid values (e.g. "O1:abc")
    return result


def _parse_outputs(args: list) -> Dict[str, str]:
    """Parse 'O1=深い認識 O2=強い意志' → {'O1': '深い認識', ...}"""
    result = {}
    for arg in args:
        if "=" in arg:
            k, v = arg.split("=", 1)
            result[k.strip()] = v.strip()
    return result


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Cone Builder — Hub Peras @converge C0-C3",
        usage="python -m mekhane.fep.cone_builder --series O O1='出力1' O2='出力2' ...",
    )
    parser.add_argument(
        "--series", "-s",
        required=True,
        choices=["O", "S", "H", "P", "K", "A"],
        help="Series to build cone for",
    )
    parser.add_argument(
        "--pw",
        default="",
        help="Precision Weighting: 'O1:0.5,O3:-0.5'",
    )
    parser.add_argument(
        "--apex",
        default=None,
        help="Pre-computed apex (integrated judgment)",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.0,
        help="Confidence score (0-100)",
    )
    parser.add_argument(
        "outputs",
        nargs="*",
        help="Theorem outputs: O1='認識の結論' O2='意志の結論' ...",
    )

    args = parser.parse_args()

    series = Series[args.series]
    pw = _parse_pw(args.pw)
    outputs = _parse_outputs(args.outputs)

    if not outputs:
        print("⚠️ No outputs provided. Use: O1='出力1' O2='出力2' ...", file=sys.stderr)
        sys.exit(1)

    cone = converge(series, outputs, pw=pw or None, apex=args.apex, confidence=args.confidence)
    print(describe_cone(cone))

