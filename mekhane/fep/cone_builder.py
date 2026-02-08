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

from difflib import SequenceMatcher
from typing import Dict, List, Optional

from mekhane.fep.category import Cone, Series, build_cone


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

    Uses pairwise text similarity to estimate how much the 4 outputs
    agree or contradict. Low dispersion = consistent Cone.

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
            ratio = SequenceMatcher(None, values[i], values[j]).ratio()
            similarities.append(ratio)

    if not similarities:
        return 0.0

    avg_similarity = sum(similarities) / len(similarities)
    return round(1.0 - avg_similarity, 3)


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
) -> Cone:
    """Execute @converge C0-C3 and return a fully populated Cone.

    This is the main entry point for Hub Peras workflows.

    Args:
        series: Which series (O/S/H/P/K/A)
        outputs: Dict mapping theorem_id -> output string
        pw: Precision Weighting dict {theorem_id: weight}.
            weight ∈ [-1, +1]. 0 = neutral, +1 = emphasize, -1 = suppress.
            None or empty = uniform weighting (equivalent to +/- operators).
        apex: Optional pre-computed integrated judgment
        confidence: Optional confidence score (0-100)

    Returns:
        Cone with C0 pw, C1 projections, C2 resolution, C3 universality

    Formula (C2 weighted fusion):
        統合出力 = Σ(定理_i × (1 + pw_i)) / Σ(1 + pw_i)
    """
    # C0: Precision Weighting
    cone_pw = pw or {}

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

    # C3: Set confidence and universality
    cone.confidence = confidence
    cone.is_universal = confidence >= 70.0  # 70% threshold for universality

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
        f"**V[outputs]** = {cone.dispersion:.3f}",
        f"**Resolution** = {cone.resolution_method}",
        f"**Apex** = {cone.apex or '(未設定)'}",
    ])

    # C3: Universality
    lines.extend([
        f"**Confidence** = {cone.confidence:.0f}%",
        f"**Universal** = {'Yes' if cone.is_universal else 'No'}",
    ])

    return "\n".join(lines)
