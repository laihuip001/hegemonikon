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
    OscillationType,
    SeriesAttractor,
    SuggestResult,
)


# ---------------------------------------------------------------------------
# AttractorAdvisor
# ---------------------------------------------------------------------------

class AttractorAdvisor:
    """
    SeriesAttractor をワークフロー推薦システムとして利用する。

    Usage:
        advisor = AttractorAdvisor()
        rec = advisor.recommend("Why does this project exist?")
        print(rec.advice)
        # → "O-series (Ousia) に収束。推薦: /noe, /bou, /zet, /ene"
    """

    def __init__(self, force_cpu: bool = False):
        self._attractor = SeriesAttractor(force_cpu=force_cpu)

    def recommend(self, user_input: str) -> Recommendation:
        """
        ユーザー入力からワークフロー推薦を生成する。

        Returns:
            Recommendation with advice text, suggested workflows,
            and oscillation diagnosis.
        """
        result = self._attractor.diagnose(user_input)

        if not result.attractors:
            return Recommendation(
                advice="引力圏外。特定の Series に収束しません。",
                workflows=[],
                series=[],
                oscillation=result.oscillation,
                confidence=0.0,
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
        )

    def format_for_llm(self, user_input: str) -> str:
        """
        LLM のシステムプロンプトに注入する形式でワークフロー推薦を返す。

        Returns:
            空文字列 (推薦なし) または "[Attractor: ...]" 形式の文字列
        """
        rec = self.recommend(user_input)

        if not rec.workflows:
            return ""

        if rec.oscillation == OscillationType.CLEAR:
            return f"[Attractor: {rec.series[0]} → {', '.join(rec.workflows)}]"
        elif rec.oscillation == OscillationType.POSITIVE:
            series_str = "+".join(rec.series)
            return f"[Attractor: {series_str} oscillating → {', '.join(rec.workflows)}]"
        else:
            return f"[Attractor: weak ({rec.series[0]}?)]"


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class Recommendation:
    """ワークフロー推薦の結果"""
    advice: str
    workflows: list[str]
    series: list[str]
    oscillation: OscillationType
    confidence: float

    def __repr__(self) -> str:
        return f"⟨Rec: {'+'.join(self.series)} | {self.oscillation.value} | conf={self.confidence:.3f}⟩"


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

    llm_format = advisor.format_for_llm(user_input)
    print(f"\nLLM 注入形式: {llm_format}")


if __name__ == "__main__":
    main()
