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

from dataclasses import dataclass, field
from typing import List, Optional

from mekhane.fep.category import Cone, Series
from mekhane.fep.cone_builder import is_uniform_pw


# =============================================================================
# ConeAdvice
# =============================================================================


@dataclass
class ConeAdvice:
    """Next-action recommendation from a Cone analysis.

    This is what makes the Cone a "consumer" type —
    structured data drives structured decisions.
    """

    action: str  # "proceed" | "investigate" | "devil" | "reweight"
    reason: str  # Human-readable justification
    suggested_wf: str = ""  # Recommended WF (e.g. "/dia devil")
    next_steps: List[str] = field(default_factory=list)
    urgency: float = 0.0  # 0.0 (低) - 1.0 (高)

    def __repr__(self) -> str:
        wf = f" → {self.suggested_wf}" if self.suggested_wf else ""
        return f"ConeAdvice({self.action}{wf}, urgency={self.urgency:.1f})"


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
    | V > 0.1 + conf < 50               | investigate | /zet or /sop |
    | PW non-uniform + resolution=pw_w.  | reweight    | /dia epo     |
    | is_universal (V≤0.1, conf≥70)      | proceed     | —            |
    | else (low dispersion, moderate)    | proceed     | —            |

    Args:
        cone: A fully populated Cone from converge()

    Returns:
        ConeAdvice with action, reason, and suggested workflow
    """
    series_name = cone.series.name

    # --- Rule 1: Serious contradiction (V > 0.3) ---
    if cone.needs_devil:
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
        )

    # --- Rule 2: S-series strategy risk (V > 0.2) ---
    if cone.series == Series.S and cone.dispersion > 0.2:
        return ConeAdvice(
            action="devil",
            reason=f"S-series + V={cone.dispersion:.2f} > 0.2: "
                   f"戦略判断の矛盾は実行リスクが高い",
            suggested_wf="/dia devil",
            next_steps=[
                "S1(尺度) と S3(基準) の矛盾を確認",
                "S2(方法) が S4(実践) と整合するか検証",
            ],
            urgency=0.8,
        )

    # --- Rule 3: Low confidence + moderate dispersion ---
    if cone.dispersion > 0.1 and cone.confidence < 50:
        # Choose WF based on series
        if cone.series in (Series.K, Series.A):
            wf = "/sop"  # K/A: 調査で解消
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
