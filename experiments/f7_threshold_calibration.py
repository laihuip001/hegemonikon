"""
S1: F7 Threshold Calibration

PURPOSE: Handoff の Doxa セクションから cosine similarity 分布を計測し、
F7 KI 昇格閾値 (現在 0.85 仮値) の最適値を実験的に決定する。
"""

import re
import sys
import json
import itertools
from pathlib import Path
from collections import Counter

# Handoff directory
HANDOFF_DIR = Path.home() / "oikos/mneme/.hegemonikon/sessions"


def extract_doxa_sections(handoff_path: Path) -> list[str]:
    """Handoff ファイルから Doxa/信念 セクションを抽出"""
    text = handoff_path.read_text(encoding="utf-8", errors="replace")
    
    # Multiple patterns for Doxa sections
    patterns = [
        r"##\s*(?:Doxa|信念|Beliefs?)[\s\S]*?(?=\n##\s|\Z)",
        r"##\s*(?:学んだこと|Lessons|insights)[\s\S]*?(?=\n##\s|\Z)",
        r"##\s*(?:発見|Discoveries)[\s\S]*?(?=\n##\s|\Z)",
    ]
    
    sections = []
    for pat in patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        sections.extend(matches)
    
    # Fallback: extract bullet points that look like beliefs
    if not sections:
        bullets = re.findall(r"^[-*]\s+.+$", text, re.MULTILINE)
        if bullets:
            sections.append("\n".join(bullets[:10]))
    
    return sections


def compute_cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Cosine similarity between two vectors"""
    import numpy as np
    a, b = np.array(vec_a), np.array(vec_b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    if norm == 0:
        return 0.0
    return float(np.dot(a, b) / norm)


def main():
    # 1. Collect all Handoff files
    handoff_files = sorted(HANDOFF_DIR.glob("handoff_*.md"))
    print(f"Found {len(handoff_files)} handoff files")
    
    # 2. Extract Doxa sections
    all_doxa: list[tuple[str, str]] = []  # (filename, text)
    for hf in handoff_files:
        sections = extract_doxa_sections(hf)
        for s in sections:
            cleaned = s.strip()
            if len(cleaned) > 20:  # Filter noise
                all_doxa.append((hf.name, cleaned))
    
    print(f"Extracted {len(all_doxa)} Doxa sections")
    
    if len(all_doxa) < 2:
        print("Not enough Doxa sections for comparison")
        sys.exit(1)
    
    # 3. Embed all sections
    sys.path.insert(0, str(Path.home() / "oikos/hegemonikon"))
    from mekhane.anamnesis.index import Embedder
    
    embedder = Embedder()
    texts = [t for _, t in all_doxa]
    
    print(f"Embedding {len(texts)} texts...")
    vectors = embedder.embed_batch(texts)
    
    # 4. Compute all pairwise similarities
    n = len(vectors)
    similarities = []
    same_session_sims = []
    cross_session_sims = []
    
    for i, j in itertools.combinations(range(n), 2):
        sim = compute_cosine_similarity(vectors[i], vectors[j])
        similarities.append(sim)
        
        # Same session vs cross session
        file_i = all_doxa[i][0]
        file_j = all_doxa[j][0]
        if file_i == file_j:
            same_session_sims.append(sim)
        else:
            cross_session_sims.append(sim)
    
    # 5. Statistics
    import numpy as np
    sims = np.array(similarities)
    
    print("\n" + "=" * 60)
    print("F7 Threshold Calibration Results")
    print("=" * 60)
    
    print(f"\nTotal pairs: {len(similarities)}")
    print(f"Mean similarity: {sims.mean():.4f}")
    print(f"Std:  {sims.std():.4f}")
    print(f"Min:  {sims.min():.4f}")
    print(f"Max:  {sims.max():.4f}")
    
    # Percentiles
    for p in [50, 75, 80, 85, 90, 95, 99]:
        print(f"P{p}: {np.percentile(sims, p):.4f}")
    
    if same_session_sims:
        ss = np.array(same_session_sims)
        print(f"\nSame-session pairs: {len(ss)}, mean: {ss.mean():.4f}")
    
    if cross_session_sims:
        cs = np.array(cross_session_sims)
        print(f"Cross-session pairs: {len(cs)}, mean: {cs.mean():.4f}")
    
    # 6. Threshold recommendation
    print("\n" + "-" * 60)
    print("Threshold Recommendation:")
    print("-" * 60)
    
    # A good threshold should be above the mean + 1 std
    # to capture only truly similar beliefs
    recommended = float(np.percentile(sims, 90))
    print(f"\nRecommended threshold: {recommended:.4f}")
    print(f"(= P90 — top 10% most similar pairs)")
    print(f"Current F7 threshold: 0.85 (provisional)")
    
    if recommended > 0.85:
        print(f"→ Current threshold is LOOSE. Consider raising to {recommended:.2f}")
    elif recommended < 0.85:
        print(f"→ Current threshold is TIGHT. Consider lowering to {recommended:.2f}")
    else:
        print(f"→ Current threshold matches empirical data")
    
    # 7. Save results
    results = {
        "total_doxa": len(all_doxa),
        "total_pairs": len(similarities),
        "mean": float(sims.mean()),
        "std": float(sims.std()),
        "min": float(sims.min()),
        "max": float(sims.max()),
        "percentiles": {str(p): float(np.percentile(sims, p)) for p in [50, 75, 80, 85, 90, 95, 99]},
        "recommended_threshold": recommended,
        "current_threshold": 0.85,
    }
    
    out_path = Path(__file__).parent / "f7_calibration_results.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
