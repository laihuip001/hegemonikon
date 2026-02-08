# PROOF: [L2/FEP] <- mekhane/fep/
# PURPOSE: Attractor 結果をワークフロー推薦に変換する
"""
Attractor Advisor

SeriesAttractor の suggest()/diagnose() 結果を、
LLM が使える自然言語のワークフロー推薦に変換する。

接続先: KERNEL_DOCTRINE の「Skill 強制参照」テーブルの置換。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from mekhane.fep.attractor import (
    OscillationDiagnosis,
    OscillationType,
    SeriesAttractor,
    SuggestResult,
    DecomposeResult,
)
from mekhane.fep.category import CognitiveType, COGNITIVE_TYPES
from mekhane.fep.cone_builder import (
    classify_cognitive_type,
    is_cross_boundary_morphism,
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

    # PURPOSE: Attractor推薦結果をWFディスパッチに変換する中間層
    def __init__(self, force_cpu: bool = False, use_gnosis: bool = True):
        self._attractor = SeriesAttractor(force_cpu=force_cpu)
        self._use_gnosis = use_gnosis

    # PURPOSE: ユーザー入力からワークフロー推薦を生成する。
    def recommend(self, user_input: str) -> Recommendation:
        """
        ユーザー入力からワークフロー推薦を生成する。

        Returns:
            Recommendation with advice text, suggested workflows,
            and oscillation diagnosis.
        """
        result = self._attractor.diagnose(user_input)
        rec = self._recommend_from_result(result)

        # Gnōsis enrichment: Attractor Series に関連する知識を付与
        if self._use_gnosis and rec.series:
            rec.knowledge_context = self._retrieve_gnosis(user_input)

        return rec

    # PURPOSE: Sophia インデックスから関連知識を検索し推薦を補強する
    def _retrieve_gnosis(self, query: str, top_k: int = 2) -> list[dict]:
        """Sophia ベクトルインデックスから関連 KI を検索する。

        Graceful degradation: index 不在やエラー時は空リストを返す。
        """
        try:
            from mekhane.symploke.sophia_ingest import (
                DEFAULT_INDEX_PATH,
                load_sophia_index,
                search_loaded_index,
            )

            if not DEFAULT_INDEX_PATH.exists():
                return []

            adapter = load_sophia_index(str(DEFAULT_INDEX_PATH))
            results = search_loaded_index(adapter, query, top_k=top_k)

            return [
                {
                    "ki_name": r.metadata.get("ki_name", "Unknown"),
                    "summary": r.metadata.get("summary", "")[:80],
                    "score": round(r.score, 3),
                }
                for r in results
            ]
        except Exception:
            return []  # Gnōsis failure should never block recommendations

    # PURPOSE: SuggestResult から Recommendation を生成する（内部ヘルパー）
    def _recommend_from_result(self, result: SuggestResult) -> Recommendation:
        """SuggestResult から Recommendation を生成する。

        recommend() と recommend_compound() の共通ロジック。
        diagnose() の再呼出しを避けるために分離。
        """
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

        # --- CognitiveType analysis ---
        cognitive_types = _classify_series_list(series_list)
        boundary_crossings = _detect_crossings(series_list)
        pw_suggestion = _suggest_pw_for_crossings(boundary_crossings, series_list)

        return Recommendation(
            advice=advice,
            workflows=unique_workflows,
            series=series_list,
            oscillation=result.oscillation,
            confidence=result.top_similarity,
            interpretation=interpretation,
            cognitive_types=cognitive_types,
            boundary_crossings=boundary_crossings,
            pw_suggestion=pw_suggestion,
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

        # Base lines
        lines: list[str] = []

        if rec.oscillation == OscillationType.CLEAR:
            lines.append(
                f"[Attractor: {rec.series[0]} → {', '.join(rec.workflows)}]"
            )
            lines.append(f"[FEP: {interp.theory}]")
        elif rec.oscillation == OscillationType.POSITIVE:
            series_str = "+".join(rec.series)
            morphisms = f" | morphisms: {', '.join(interp.morphisms)}" if interp.morphisms else ""
            lines.append(
                f"[Attractor: {series_str} oscillating → {', '.join(rec.workflows)}]"
            )
            lines.append(f"[FEP: {interp.theory}]")
            lines.append(f"[Action: {interp.action}{morphisms}]")
        else:
            lines.append(f"[Attractor: weak ({rec.series[0]}?)]")
            lines.append(f"[FEP: {interp.theory}]")
            lines.append(f"[Action: {interp.action}]")

        # CognitiveType line (Task 3 enrichment)
        if rec.cognitive_types:
            ct_str = ", ".join(
                f"{s}={t}" for s, t in rec.cognitive_types.items()
            )
            lines.append(f"[CognitiveType: {ct_str}]")

        # Boundary crossing + PW boost (Task 3 enrichment)
        if rec.boundary_crossings:
            cross_str = ", ".join(rec.boundary_crossings)
            lines.append(f"[Boundary: {cross_str}]")
        if rec.pw_suggestion:
            pw_str = ", ".join(
                f"{k}={v:+.1f}" for k, v in rec.pw_suggestion.items()
            )
            lines.append(f"[PW boost: {pw_str}]")

        # Gnōsis knowledge context
        if rec.knowledge_context:
            ki_names = ", ".join(k["ki_name"] for k in rec.knowledge_context)
            lines.append(f"[Knowledge: {ki_names}]")

        return "\n".join(lines)

    # PURPOSE: Problem D — 複合入力を分解して各セグメントごとに推薦する
    def recommend_compound(self, user_input: str) -> CompoundRecommendation:
        """複合入力を文分解し、各セグメントごとに推薦を生成する。

        単一文の場合は通常の recommend() に委譲。
        複数文の場合は decompose() → 各セグメントごとに推薦 → マージ。

        最適化: decompose() は内部で diagnose() を呼ぶため、
        その SuggestResult を _recommend_from_result() で再利用し、
        diagnose() の重複呼出を排除 (2N → N)。

        Returns:
            CompoundRecommendation with per-segment and merged recommendations
        """
        decomp = self._attractor.decompose(user_input)

        # decompose() の SuggestResult をそのまま使い、diagnose() 再呼出しを避ける
        segments: list[tuple[str, Recommendation]] = []
        for seg in decomp.segments:
            rec = self._recommend_from_result(seg.diagnosis)
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
            is_multi_segment=len(decomp.segments) > 1,
            primary=best_rec,
        )



# ---------------------------------------------------------------------------
# CognitiveType Analysis Helpers (Task 3: Attractor → CognitiveType → PW)
# ---------------------------------------------------------------------------

# Series → representative theorem (first theorem of each series)
_SERIES_FIRST_THEOREM = {
    "O": "O1", "S": "S1", "H": "H1", "P": "P1", "K": "K1", "A": "A1",
}


def _classify_series_list(series_list: list[str]) -> Dict[str, str]:
    """Classify each series by its primary CognitiveType.

    Maps series letter → CognitiveType value string.
    Uses the first theorem of each series as representative.

    Returns:
        e.g. {"O": "understanding", "S": "reasoning"}
    """
    result = {}
    for s in series_list:
        theorem_id = _SERIES_FIRST_THEOREM.get(s)
        if theorem_id:
            ct = COGNITIVE_TYPES.get(theorem_id)
            if ct:
                result[s] = ct.value
    return result


def _detect_crossings(series_list: list[str]) -> List[str]:
    """Detect U/R boundary crossings between recommended series.

    When multiple series are recommended (oscillation), checks if they
    cross the Understanding/Reasoning boundary.

    Returns:
        List of crossing strings, e.g. ["U→R", "R→U"]
    """
    if len(series_list) < 2:
        return []

    crossings = []
    seen = set()
    for i, s1 in enumerate(series_list):
        for s2 in series_list[i + 1:]:
            t1 = _SERIES_FIRST_THEOREM.get(s1)
            t2 = _SERIES_FIRST_THEOREM.get(s2)
            if t1 and t2:
                crossing = is_cross_boundary_morphism(t1, t2)
                if crossing and crossing not in seen:
                    seen.add(crossing)
                    crossings.append(crossing)
    return crossings


def _suggest_pw_for_crossings(
    crossings: List[str],
    series_list: list[str],
) -> Dict[str, float]:
    """Suggest PW adjustments when U/R boundary crossings are detected.

    When an attractor recommendation spans both Understanding and Reasoning
    series, the Bridge theorems (A1, A3) should have elevated PW to
    facilitate the transition.

    Strategy:
    - U→R crossing: boost A1 (Pathos) — the U→R bridge
    - R→U crossing: boost A3 (Gnōmē) — the R→U bridge
    - Both: boost both bridges + K4 (Sophia, mixed)

    Returns:
        Dict of theorem_id → suggested PW adjustment (e.g. {"A1": 0.5})
        Empty dict if no crossings.
    """
    if not crossings:
        return {}

    suggestion: Dict[str, float] = {}

    if "U→R" in crossings:
        # Boost A1 (Pathos) — the Understanding → Reasoning bridge
        suggestion["A1"] = 0.5
    if "R→U" in crossings:
        # Boost A3 (Gnōmē) — the Reasoning → Understanding bridge
        suggestion["A3"] = 0.5
    if len(crossings) >= 2:
        # Both directions: activate the mixed theorem (Sophia = wisdom)
        suggestion["K4"] = 0.3

    return suggestion


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
    # Task 3: CognitiveType integration
    cognitive_types: Dict[str, str] = field(default_factory=dict)  # series→type
    boundary_crossings: List[str] = field(default_factory=list)  # e.g. ["U→R"]
    pw_suggestion: Dict[str, float] = field(default_factory=dict)  # PW adjustments
    # Gnōsis knowledge context: related KI items
    knowledge_context: List[dict] = field(default_factory=list)

    # PURPOSE: 推薦結果の概要を表示（WF名+理由）
    def __repr__(self) -> str:
        cross = f" [{','.join(self.boundary_crossings)}]" if self.boundary_crossings else ""
        return f"⟨Rec: {'+'.join(self.series)} | {self.oscillation.value} | conf={self.confidence:.3f}{cross}⟩"


# PURPOSE: Problem D — 複合入力の推薦結果
@dataclass
class CompoundRecommendation:
    """複合入力の推薦結果: 各セグメント + マージされたワークフロー"""
    segments: list[tuple[str, Recommendation]]  # (text, recommendation) pairs
    merged_series: list[str]
    merged_workflows: list[str]
    is_compound: bool  # 複数 Series に分解されたか (= is_multi_series)
    is_multi_segment: bool  # 複数文に分解されたか
    primary: Recommendation | None  # 最高確信度の推薦

    # PURPOSE: 分解推薦結果の概要を表示（セグメント数+統合WF）
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
