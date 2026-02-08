# PROOF: [L2/ユーティリティ] <- mekhane/fep/
"""
PROOF: [L2/ユーティリティ] このファイルは存在しなければならない

A0 → Hub Peras WF (@converge) で Cone を計算する必要がある
   → V[outputs] (分散度) を自動計算し、解消法を提案する
   → cone_builder.py が担う

Q.E.D.

---

Cone Builder — Hub Peras @converge 支援ユーティリティ

Hub WF (/o, /s, /h, /p, /k, /a) の @converge C1-C3 を支援する。
build_cone() で Cone を構築し、compute_dispersion() で V[outputs] を計算、
resolve_method() で解消法を判定する。

Usage:
    from mekhane.fep.cone_builder import converge

    result = converge(
        series=Series.O,
        outputs={"O1": "深い認識", "O2": "強い意志", "O3": "鋭い問い", "O4": "確実な行動"}
    )
    print(result.apex)            # 統合判断
    print(result.dispersion)      # V[outputs]
    print(result.resolution_method)  # simple/weighted/root
"""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

from mekhane.fep.category import Cone, Series, build_cone


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


# PURPOSE: @converge C2 — Cone の頂点探索 (Resolve): 解消法を判定する
def resolve_method(dispersion: float) -> str:
    """Determine resolution method based on V[outputs].

    Returns:
        str: "simple" (≤0.1), "weighted" (≤0.3), or "root" (>0.3)
    """
    if dispersion <= 0.1:
        return "simple"
    elif dispersion <= 0.3:
        return "weighted"
    else:
        return "root"


# PURPOSE: @converge C1-C3 を一括実行する
def converge(
    series: Series,
    outputs: Dict[str, str],
    apex: Optional[str] = None,
    confidence: float = 0.0,
) -> Cone:
    """Execute @converge C1-C3 and return a fully populated Cone.

    This is the main entry point for Hub Peras workflows.

    Args:
        series: Which series (O/S/H/P/K/A)
        outputs: Dict mapping theorem_id -> output string
        apex: Optional pre-computed integrated judgment
        confidence: Optional confidence score (0-100)

    Returns:
        Cone with C1 projections, C2 resolution, and C3 universality
    """
    # C1: Build Cone with projections
    cone = build_cone(series, outputs)

    # C1: Compute dispersion
    cone.dispersion = compute_dispersion(outputs)

    # C2: Determine resolution method
    cone.resolution_method = resolve_method(cone.dispersion)

    # C2: Set apex if provided
    if apex:
        cone.apex = apex

    # C3: Set confidence and universality
    cone.confidence = confidence
    cone.is_universal = confidence >= 70.0  # 70% threshold for universality

    return cone


# PURPOSE: 全 Series の圏論的位置を表示するユーティリティ
def describe_cone(cone: Cone) -> str:
    """Format a Cone as human-readable text for WF output."""
    lines = [
        f"## Cone: {cone.series.value}-series",
        "",
        "| Theorem | Hom Label | Output |",
        "|:--------|:----------|:-------|",
    ]
    for proj in cone.projections:
        lines.append(f"| {proj.theorem_id} | {proj.hom_label} | {proj.output} |")

    lines.extend([
        "",
        f"**V[outputs]** = {cone.dispersion:.3f}",
        f"**Resolution** = {cone.resolution_method}",
        f"**Apex** = {cone.apex or '(未設定)'}",
        f"**Confidence** = {cone.confidence:.0f}%",
        f"**Universal** = {'Yes' if cone.is_universal else 'No'}",
    ])

    return "\n".join(lines)
