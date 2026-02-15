"""
F6: KI Auto-Promotion PoC

PURPOSE: /bye 時に呼び出される KI (Knowledge Item) 昇格候補の自動提案。
Doxa (信念) の中から繰り返し出現するものを検出し、KI への昇格を推薦する。

Algorithm:
1. 最新 N 件の Handoff から Doxa セクションを抽出
2. 各 Doxa を embedding
3. Similarity ≥ THRESHOLD (0.60) のペアをカウント
4. MIN_FREQUENCY (5) 回以上出現 → 昇格候補
5. BC-6 確信度ラベルで重み付け
6. スコア上位の候補を返す

Usage from /bye:
    from experiments.ki_promotion_poc import suggest_ki_promotions
    candidates = suggest_ki_promotions(max_candidates=5)
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

HANDOFF_DIR = Path.home() / "oikos/mneme/.hegemonikon/sessions"
# S1 calibrated values
SIMILARITY_THRESHOLD = 0.60
MIN_FREQUENCY = 5


def extract_doxa_sections(handoff_path: Path) -> list[str]:
    """Handoff から Doxa/信念セクションの各項目を抽出"""
    text = handoff_path.read_text(encoding="utf-8", errors="replace")

    patterns = [
        r"##\s*(?:Doxa|信念|Beliefs?)[\s\S]*?(?=\n##\s|\Z)",
        r"##\s*(?:学んだこと|Lessons|insights)[\s\S]*?(?=\n##\s|\Z)",
    ]

    sections = []
    for pat in patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        sections.extend(matches)

    # Extract individual bullet points as separate beliefs
    beliefs = []
    for section in sections:
        bullets = re.findall(r"^[-*]\s+(.+)$", section, re.MULTILINE)
        beliefs.extend([b.strip() for b in bullets if len(b.strip()) > 20])

    return beliefs


def extract_confidence(belief_text: str) -> float:
    """BC-6 確信度ラベルから重みを推定"""
    if "[確信]" in belief_text or "90%" in belief_text:
        return 1.0
    elif "[推定]" in belief_text or "60-90%" in belief_text:
        return 0.5
    elif "[仮説]" in belief_text or "<60%" in belief_text:
        return 0.1
    return 0.5  # Default: 推定


def suggest_ki_promotions(
    max_candidates: int = 5,
    lookback: int = 50,
) -> list[dict]:
    """
    KI 昇格候補を返す。

    Args:
        max_candidates: 返す候補の最大数
        lookback: 何件の Handoff を遡るか

    Returns:
        [{text, frequency, confidence, score, sources}]
    """
    # 1. Collect beliefs from recent handoffs
    handoff_files = sorted(HANDOFF_DIR.glob("handoff_*.md"))[-lookback:]
    if not handoff_files:
        return []

    all_beliefs: list[tuple[str, str]] = []  # (belief_text, handoff_filename)
    for hf in handoff_files:
        beliefs = extract_doxa_sections(hf)
        for b in beliefs:
            all_beliefs.append((b, hf.name))

    if len(all_beliefs) < 2:
        return []

    # 2. Embed and compute similarities
    sys.path.insert(0, str(Path.home() / "oikos/hegemonikon"))
    from mekhane.anamnesis.index import Embedder
    import numpy as np

    embedder = Embedder()
    texts = [b[0] for b in all_beliefs]
    vectors = embedder.embed_batch(texts)

    # 3. Group similar beliefs
    n = len(vectors)
    clusters: dict[int, list[int]] = defaultdict(list)
    assigned = set()

    for i in range(n):
        if i in assigned:
            continue
        cluster = [i]
        assigned.add(i)
        for j in range(i + 1, n):
            if j in assigned:
                continue
            # Cosine similarity
            a, b_vec = np.array(vectors[i]), np.array(vectors[j])
            norm = np.linalg.norm(a) * np.linalg.norm(b_vec)
            if norm > 0:
                sim = float(np.dot(a, b_vec) / norm)
                if sim >= SIMILARITY_THRESHOLD:
                    cluster.append(j)
                    assigned.add(j)
        clusters[i] = cluster

    # 4. Filter by MIN_FREQUENCY
    candidates = []
    for rep_idx, members in clusters.items():
        if len(members) < MIN_FREQUENCY:
            continue

        # Representative text = the one from the most recent handoff
        rep_text = all_beliefs[rep_idx][0]
        sources = list(set(all_beliefs[m][1] for m in members))
        avg_confidence = sum(extract_confidence(all_beliefs[m][0]) for m in members) / len(members)

        # Score = frequency * confidence
        score = len(members) * avg_confidence

        candidates.append({
            "text": rep_text[:200],
            "frequency": len(members),
            "confidence": round(avg_confidence, 2),
            "score": round(score, 2),
            "sources": sources[:5],  # Show up to 5 source handoffs
        })

    # 5. Sort by score, return top N
    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates[:max_candidates]


def format_promotion_report(candidates: list[dict]) -> str:
    """昇格候補をフォーマット"""
    if not candidates:
        return "✅ KI 昇格候補なし (閾値 0.60, 最低頻度 5)"

    lines = [
        "🔄 **KI 昇格候補** — 繰り返し出現する Doxa:",
        "",
    ]

    for i, c in enumerate(candidates, 1):
        lines.extend([
            f"**{i}. [{c['frequency']}回, score={c['score']}]** {c['text']}",
            f"   確信度: {c['confidence']}, ソース: {', '.join(c['sources'][:3])}",
            "",
        ])

    lines.append("> `[y]` で KI に昇格、`[n]` でスキップ")
    return "\n".join(lines)


if __name__ == "__main__":
    print("F6: KI Auto-Promotion PoC")
    print("=" * 60)

    candidates = suggest_ki_promotions(max_candidates=10)
    print(format_promotion_report(candidates))
