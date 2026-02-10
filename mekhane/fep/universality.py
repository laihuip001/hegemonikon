# PROOF: [L1/定理] <- mekhane/fep/ A0→圏論的普遍性検証(Kalon)→美の評価基盤
"""
Kalon — 圏論的普遍性検証モジュール

τὸ καλόν = 美。余分がなく不足もない。普遍的解はそれ自体が美しい。

F: Cat → Noe — 圏論の概念を /noe の思考プロセスに関手する。
/noe PHASE 3 (Kalon) で使用。

Usage:
    from mekhane.fep.universality import kalon_verify, KalonResult

    candidates = {
        "V1": "リソース無限なら全自動化",
        "V2": "機能削減で本質に集中",
        "V3": "業界タブーを破壊",
        "V4": "データ駆動で最適化",
        "Synthesis": "本質を自動化し、破壊的効率を実現",
    }
    result = kalon_verify(candidates)
    print(result.kalon_score)        # 0.75
    print(result.universal_candidate) # "Synthesis"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data Types
# ---------------------------------------------------------------------------

@dataclass
class FactorizationResult:
    """因子分解テストの結果: 候補 A は候補 B の特殊ケースか？

    圏論的意味: 射 h: B → A が存在し、f_i = h ∘ u を満たすか。
    """
    source: str           # candidate A (potentially more specific)
    target: str           # candidate B (potentially more general)
    factorizable: bool    # A is a special case of B
    reasoning: str        # LLM judgment rationale
    confidence: float     # 0.0 - 1.0


@dataclass
class KalonResult:
    """Kalon 検証の最終結果

    圏論的意味: Limit の apex (頂点) = 普遍的候補。
    Kalon スコア = 普遍性の強さ（余分な仮定の少なさ）。
    """
    universal_candidate: str                   # Limit の apex
    factorizations: List[FactorizationResult]   # 全ペアの因子分解結果
    kalon_score: float                         # 0.0 - 1.0
    beauty_statement: str                      # 美の1行記述
    uniqueness: str                            # HIGH / MED / LOW
    diagram: Dict[str, List[str]] = field(default_factory=dict)  # 候補 → 特殊化先


# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------

def build_kalon_prompt(candidates: Dict[str, str]) -> str:
    """因子分解テスト用の一括 LLM プロンプトを生成。

    全候補ペアの包含関係を一度に判定するための構造化プロンプト。
    精度優先: テキスト包含率ではなく LLM に意味的な「特殊化の射」を判定させる。

    Args:
        candidates: {候補名: 候補内容} の辞書

    Returns:
        LLM に送信するプロンプト文字列
    """
    names = list(candidates.keys())
    pairs = []
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            if i < j:
                pairs.append((a, b))

    lines = [
        "以下の候補解について、包含関係（特殊化の射）を判定してください。",
        "",
        "## 候補解一覧",
    ]
    for name, content in candidates.items():
        lines.append(f"### {name}")
        lines.append(content)
        lines.append("")

    lines.append("## 判定タスク")
    lines.append("")
    lines.append("各ペアについて、一方が他方の **特殊ケース** かを判定してください。")
    lines.append("「特殊ケース」とは: より一般的な方に特定の条件を加えると、")
    lines.append("より具体的な方に退化（特殊化）すること。")
    lines.append("")

    for idx, (a, b) in enumerate(pairs, 1):
        lines.append(f"### ペア {idx}: {a} ↔ {b}")
        lines.append(f"Q1: {a} は {b} の特殊ケースか？ → YES/NO + 理由")
        lines.append(f"Q2: {b} は {a} の特殊ケースか？ → YES/NO + 理由")
        lines.append("")

    lines.append("## 出力形式")
    lines.append("各ペアについて以下の JSON 配列を返してください:")
    lines.append("```json")
    lines.append('[')
    lines.append('  {"source": "A", "target": "B", "factorizable": true/false, '
                 '"reasoning": "理由", "confidence": 0.8},')
    lines.append('  ...')
    lines.append(']')
    lines.append("```")

    return "\n".join(lines)


def parse_kalon_response(
    response: str, candidates: Dict[str, str]
) -> List[FactorizationResult]:
    """LLM の因子分解応答をパースして FactorizationResult リストに変換。

    LLM が JSON 配列を返すことを期待するが、
    フォールバックとして YES/NO パターンも検出する。

    Args:
        response: LLM 応答テキスト
        candidates: 元の候補辞書（バリデーション用）

    Returns:
        FactorizationResult のリスト
    """
    import json
    import re

    results: List[FactorizationResult] = []

    # Try JSON parse first
    json_match = re.search(r'\[[\s\S]*?\]', response)
    if json_match:
        try:
            data = json.loads(json_match.group())
            for item in data:
                results.append(FactorizationResult(
                    source=item.get("source", ""),
                    target=item.get("target", ""),
                    factorizable=bool(item.get("factorizable", False)),
                    reasoning=item.get("reasoning", ""),
                    confidence=float(item.get("confidence", 0.5)),
                ))
            return results
        except (json.JSONDecodeError, KeyError, TypeError):
            pass  # Fall through to pattern matching

    # Fallback: pattern matching
    names = list(candidates.keys())
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            if i < j:
                # Look for "A は B の特殊ケース: YES" patterns
                pattern_ab = re.search(
                    rf'{re.escape(a)}.*?{re.escape(b)}.*?(YES|NO)',
                    response, re.IGNORECASE
                )
                if pattern_ab:
                    results.append(FactorizationResult(
                        source=a, target=b,
                        factorizable=pattern_ab.group(1).upper() == "YES",
                        reasoning="pattern-matched",
                        confidence=0.5,
                    ))
                pattern_ba = re.search(
                    rf'{re.escape(b)}.*?{re.escape(a)}.*?(YES|NO)',
                    response, re.IGNORECASE
                )
                if pattern_ba:
                    results.append(FactorizationResult(
                        source=b, target=a,
                        factorizable=pattern_ba.group(1).upper() == "YES",
                        reasoning="pattern-matched",
                        confidence=0.5,
                    ))

    return results


def find_universal_candidate(
    candidates: Dict[str, str],
    factorizations: List[FactorizationResult],
) -> Tuple[str, str, Dict[str, List[str]]]:
    """全候補への射を持つ普遍的候補を特定する。

    圏論的意味: Limit の apex = 他の全候補を「特殊ケースとして含む」候補。
    つまり、最も多くの候補 X について f: universal → X が存在する候補。

    Args:
        candidates: 候補辞書
        factorizations: 因子分解結果

    Returns:
        (universal_candidate_name, uniqueness, diagram)
        uniqueness: HIGH (全候補)/MED (半数以上)/LOW (半数未満)
        diagram: {候補名: [特殊化先のリスト]}
    """
    names = list(candidates.keys())
    n = len(names)

    # Build diagram: target → [sources it generalizes]
    # If factorizable=True for (source=A, target=B), then A is a special case of B
    # So B "generalizes" A, meaning B → A is a specialization arrow
    generalization_count: Dict[str, int] = {name: 0 for name in names}
    diagram: Dict[str, List[str]] = {name: [] for name in names}

    for f in factorizations:
        if f.factorizable and f.confidence >= 0.3:
            # target generalizes source: target is more general
            generalization_count[f.target] = generalization_count.get(f.target, 0) + 1
            diagram[f.target].append(f.source)

    # Find the most universal candidate (most generalizations)
    if not generalization_count:
        return names[0] if names else "", "LOW", diagram

    best = max(generalization_count, key=generalization_count.get)  # type: ignore[arg-type]
    count = generalization_count[best]
    max_possible = n - 1  # can't generalize itself

    if max_possible == 0:
        uniqueness = "LOW"
    elif count >= max_possible:
        uniqueness = "HIGH"
    elif count >= max_possible / 2:
        uniqueness = "MED"
    else:
        uniqueness = "LOW"

    return best, uniqueness, diagram


def kalon_score(
    universal: str,
    candidates: Dict[str, str],
    diagram: Dict[str, List[str]],
) -> float:
    """経済性スコア (Kalon) を計算する。

    Kalon = (射の数) / (最大可能射の数)
    余分な仮定が少ないほど高い。

    Args:
        universal: 普遍的候補名
        candidates: 候補辞書
        diagram: 包含関係図

    Returns:
        0.0 - 1.0 の Kalon スコア
    """
    n = len(candidates)
    if n <= 1:
        return 1.0

    max_possible = n - 1  # universal → all others
    actual = len(diagram.get(universal, []))

    return actual / max_possible if max_possible > 0 else 0.0


def kalon_verify(
    candidates: Dict[str, str],
    factorizations: Optional[List[FactorizationResult]] = None,
) -> KalonResult:
    """Kalon 検証のエントリポイント。

    PHASE 3 のメインロジック。LLM 判定なしで動作するバージョン
    (factorizations を直接渡す場合)。

    LLM 判定込みの場合は build_kalon_prompt() → LLM → parse_kalon_response() →
    kalon_verify(candidates, parsed_results) の流れで使用。

    Args:
        candidates: {候補名: 候補内容} の辞書
        factorizations: 因子分解結果（None の場合は空リスト）

    Returns:
        KalonResult
    """
    if factorizations is None:
        factorizations = []

    universal, uniqueness, diagram = find_universal_candidate(
        candidates, factorizations
    )

    score = kalon_score(universal, candidates, diagram)

    # Generate beauty statement
    n_arrows = len(diagram.get(universal, []))
    n_total = len(candidates) - 1
    n_excess = n_total - n_arrows
    if n_excess == 0:
        beauty = f"全ての候補を包含する完全な普遍解"
    elif n_excess == 1:
        beauty = f"1つの独立候補を除き、ほぼ完全な普遍解"
    else:
        beauty = f"{n_excess}つの候補が独立。部分的な普遍性"

    return KalonResult(
        universal_candidate=universal,
        factorizations=factorizations,
        kalon_score=score,
        beauty_statement=beauty,
        uniqueness=uniqueness,
        diagram=diagram,
    )


def format_kalon_output(result: KalonResult) -> str:
    """KalonResult を /noe PHASE 3 の出力形式にフォーマット。

    Returns:
        フォーマットされた文字列
    """
    lines = ["┌─[PHASE 3: Kalon (普遍性検証)]──────────────┐"]
    lines.append("│ 図式:                                       │")

    for target, sources in result.diagram.items():
        if target == result.universal_candidate:
            for src in sources:
                lines.append(f"│   {src} ─→ {target}: 特殊化"
                             f"                         │")
        else:
            if not sources and target != result.universal_candidate:
                lines.append(f"│   {target} ─⊥─ {result.universal_candidate}:"
                             f" 独立                          │")

    lines.append("│                                              │")
    lines.append(f"│ 普遍的候補: {result.universal_candidate}"
                 f"                        │")

    n_total = sum(len(v) for v in result.diagram.values())
    lines.append(f"│   射: {n_total}, 一意性: {result.uniqueness}"
                 f"                       │")
    lines.append(f"│ Kalon: {result.kalon_score:.2f}"
                 f" — {result.beauty_statement}                  │")
    lines.append(f"│ 美: 「{result.beauty_statement}」"
                 f"                 │")
    lines.append("└───────────────────────────────────────────────┘")

    return "\n".join(lines)
