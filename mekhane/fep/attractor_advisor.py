# PROOF: [L2/FEP] <- mekhane/fep/
# PURPOSE: Attractor 結果をワークフロー推薦に変換する
"""
Attractor Advisor

SeriesAttractor の suggest()/diagnose() 結果を、
LLM が使える自然言語のワークフロー推薦に変換する。

接続先: KERNEL_DOCTRINE の「Skill 強制参照」テーブルの置換。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from mekhane.fep.attractor import (
    OscillationDiagnosis,
    OscillationType,
    SeriesAttractor,
    SuggestResult,
    DecomposeResult,
)


# ---------------------------------------------------------------------------
# AttractorAdvisor
# ---------------------------------------------------------------------------

# PURPOSE: SeriesAttractor をワークフロー推薦システムとして利用する。
class AttractorAdvisor:
    """
    SeriesAttractor をワークフロー推薦システムとして利用する。

    Usage:
        advisor = AttractorAdvisor()
        rec = advisor.recommend("Why does this project exist?")
        print(rec.advice)
        # → "O-series (Ousia) に収束。推薦: /noe, /bou, /zet, /ene"
    """

    # PURPOSE: 内部処理: init__
    def __init__(self, force_cpu: bool = False):
        self._attractor = SeriesAttractor(force_cpu=force_cpu)

    # PURPOSE: ユーザー入力からワークフロー推薦を生成する。
    def recommend(self, user_input: str) -> Recommendation:
        """
        ユーザー入力からワークフロー推薦を生成する。

        Returns:
            Recommendation with advice text, suggested workflows,
            and oscillation diagnosis.
        """
        result = self._attractor.diagnose(user_input)
        interpretation = result.interpretation

        if not result.attractors:
            return Recommendation(
                advice="引力圏外。特定の Series に収束しません。",
                workflows=[],
                series=[],
                oscillation=result.oscillation,
                confidence=0.0,
                interpretation=interpretation,
            )

        primary = result.primary
        series_list = [r.series for r in result.attractors]
        all_workflows = []
        for r in result.attractors:
            all_workflows.extend(r.workflows)
        # 重複排除しつつ順序保持
        seen = set()
        unique_workflows = []
        for wf in all_workflows:
            if wf not in seen:
                seen.add(wf)
                unique_workflows.append(wf)

        # Advice テキスト生成
        if result.oscillation == OscillationType.CLEAR:
            advice = (
                f"{primary.series}-series ({primary.name}) に明確に収束。"
                f"推薦: {', '.join(primary.workflows)}"
            )
        elif result.oscillation == OscillationType.POSITIVE:
            series_names = " + ".join(
                f"{r.series}({r.name})" for r in result.attractors
            )
            advice = (
                f"多面的入力。{series_names} が共鳴。"
                f"推薦: {', '.join(unique_workflows)}"
            )
        elif result.oscillation == OscillationType.NEGATIVE:
            advice = (
                f"Basin 未分化。{primary.series}-series が最近接だが引力が弱い。"
                f"入力をより具体的にすると収束が改善します。"
            )
        else:  # WEAK
            advice = "引力圏外。特定の Series に収束しません。"

        return Recommendation(
            advice=advice,
            workflows=unique_workflows,
            series=series_list,
            oscillation=result.oscillation,
            confidence=result.top_similarity,
            interpretation=interpretation,
        )

    # PURPOSE: LLM のシステムプロンプトに注入する形式でワークフロー推薦を返す。
    def format_for_llm(self, user_input: str) -> str:
        """
        LLM のシステムプロンプトに注入する形式でワークフロー推薦を返す。

        Returns:
            空文字列 (推薦なし) または "[Attractor: ...]" 形式の文字列
        """
        rec = self.recommend(user_input)

        if not rec.workflows:
            return ""

        interp = rec.interpretation

        if rec.oscillation == OscillationType.CLEAR:
            return (
                f"[Attractor: {rec.series[0]} → {', '.join(rec.workflows)}]\n"
                f"[FEP: {interp.theory}]"
            )
        elif rec.oscillation == OscillationType.POSITIVE:
            series_str = "+".join(rec.series)
            morphisms = f" | morphisms: {', '.join(interp.morphisms)}" if interp.morphisms else ""
            return (
                f"[Attractor: {series_str} oscillating → {', '.join(rec.workflows)}]\n"
                f"[FEP: {interp.theory}]\n"
                f"[Action: {interp.action}{morphisms}]"
            )
        else:
            return (
                f"[Attractor: weak ({rec.series[0]}?)]\n"
                f"[FEP: {interp.theory}]\n"
                f"[Action: {interp.action}]"
            )

    # PURPOSE: Problem D — 複合入力を分解して各セグメントごとに推薦する
    def recommend_compound(self, user_input: str) -> CompoundRecommendation:
        """複合入力を文分解し、各セグメントごとに推薦を生成する。

        単一文の場合は通常の recommend() に委譲。
        複数文の場合は decompose() → 各セグメントごとに推薦 → マージ。

        Returns:
            CompoundRecommendation with per-segment and merged recommendations
        """
        decomp = self._attractor.decompose(user_input)

        segments: list[tuple[str, Recommendation]] = []
        for seg in decomp.segments:
            rec = self.recommend(seg.text)
            segments.append((seg.text, rec))

        # マージ: 全 workflows を統合
        all_workflows: list[str] = []
        seen: set[str] = set()
        for _, rec in segments:
            for wf in rec.workflows:
                if wf not in seen:
                    seen.add(wf)
                    all_workflows.append(wf)

        # 最高確信度の Recommendation を primary に
        best_rec = max(segments, key=lambda x: x[1].confidence)[1] if segments else None

        return CompoundRecommendation(
            segments=segments,
            merged_series=decomp.merged_series,
            merged_workflows=all_workflows,
            is_compound=decomp.is_multi,
            primary=best_rec,
        )


# ---------------------------------------------------------------------------
# Data Classes
# PURPOSE: ワークフロー推薦の結果
# ---------------------------------------------------------------------------

@dataclass
class Recommendation:
    """ワークフロー推薦の結果"""
    advice: str
    workflows: list[str]
    series: list[str]
    oscillation: OscillationType
    confidence: float
    interpretation: OscillationDiagnosis  # Problem B: FEP 理論的解釈

    # PURPOSE: 内部処理: repr__
    def __repr__(self) -> str:
        return f"⟨Rec: {'+'.join(self.series)} | {self.oscillation.value} | conf={self.confidence:.3f}⟩"


# PURPOSE: Problem D — 複合入力の推薦結果
@dataclass
class CompoundRecommendation:
    """複合入力の推薦結果: 各セグメント + マージされたワークフロー"""
    segments: list[tuple[str, Recommendation]]  # (text, recommendation) pairs
    merged_series: list[str]
    merged_workflows: list[str]
    is_compound: bool  # 複数 Series に分解されたか
    primary: Recommendation | None  # 最高確信度の推薦

    # PURPOSE: 内部処理: repr__
    def __repr__(self) -> str:
        return (
            f"⟨Compound: {'+'.join(self.merged_series)} | "
            f"{len(self.segments)} segments | "
            f"{len(self.merged_workflows)} WFs⟩"
        )


# PURPOSE: CLI: python -m mekhane.fep.attractor_advisor "入力テキスト"
# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI: python -m mekhane.fep.attractor_advisor "入力テキスト" """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m mekhane.fep.attractor_advisor <input_text>")
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])
    advisor = AttractorAdvisor()

    print(f"\n入力: {user_input}")
    print("=" * 60)

    rec = advisor.recommend(user_input)
    print(f"\n推薦: {rec.advice}")
    print(f"Oscillation: {rec.oscillation.value}")
    print(f"Confidence: {rec.confidence:.3f}")
    print(f"Workflows: {', '.join(rec.workflows)}")

    # Problem B: 理論的解釈
    interp = rec.interpretation
    print(f"\n--- FEP 解釈 ---")
    print(f"Theory: {interp.theory}")
    print(f"Action: {interp.action}")
    if interp.morphisms:
        print(f"X-series: {', '.join(interp.morphisms)}")
    print(f"Confidence mod: {interp.confidence_modifier:+.1f}")

    llm_format = advisor.format_for_llm(user_input)
    print(f"\nLLM 注入形式:\n{llm_format}")


if __name__ == "__main__":
    main()
