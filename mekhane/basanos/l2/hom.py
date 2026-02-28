# PROOF: [L2/機能] <- mekhane/basanos/ A0->Auto->AddedByCI
# PURPOSE: Hom 計算 — 3段階の関連性尺度で随伴条件の「破れ」を測定する
# REASON: F⊣G 随伴の Hom(F(ext), hgk) ≅ Hom(ext, G(hgk)) の妥当性を定量化する
"""Hom computation for Basanos L2.

Three-pass relatedness measurement:
- Pass 1: Keyword overlap (Jaccard coefficient) — fast, deterministic
- Pass 2: Embedding similarity via Mnēmē — medium, semantic
- Pass 3: LLM judgment — slow, high precision (edge cases only)
"""

from __future__ import annotations

import subprocess
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class HomScore:
    """Result of Hom computation between two concepts."""

    source: str  # e.g., paper title or keyword
    target: str  # e.g., HGK concept or theorem ID
    keyword_score: float  # Pass 1: Jaccard coefficient [0, 1]
    embedding_score: Optional[float] = None  # Pass 2: cosine similarity [0, 1]
    llm_score: Optional[float] = None  # Pass 3: LLM judgment [0, 1]

    @property
    def combined_score(self) -> float:
        """Weighted combination of available scores."""
        scores: list[tuple[float, float]] = [(self.keyword_score, 0.3)]
        if self.embedding_score is not None:
            scores.append((self.embedding_score, 0.5))
        if self.llm_score is not None:
            scores.append((self.llm_score, 0.2))

        total_weight = sum(w for _, w in scores)
        return sum(s * w for s, w in scores) / total_weight if total_weight > 0 else 0.0

    @property
    def is_related(self) -> bool:
        """Whether the concepts are considered related (threshold: 0.3)."""
        return self.combined_score >= 0.3


class HomCalculator:
    """Calculate Hom (relatedness) between external and HGK concepts.

    Uses 3-pass architecture:
    1. Keyword overlap (always)
    2. Mnēmē embedding similarity (if available)
    3. LLM judgment (edge cases only)
    """

    def __init__(
        self,
        project_root: Path | str,
        use_mneme: bool = True,
        use_llm: bool = False,
    ) -> None:
        self.project_root = Path(project_root)
        self.use_mneme = use_mneme
        self.use_llm = use_llm

    def compute(
        self,
        source_keywords: list[str],
        target_keywords: list[str],
        source_label: str = "",
        target_label: str = "",
    ) -> HomScore:
        """Compute Hom score between two keyword sets.

        Args:
            source_keywords: External concept keywords
            target_keywords: HGK concept keywords
            source_label: Label for source (for display)
            target_label: Label for target (for display)

        Returns:
            HomScore with available passes filled in
        """
        # Pass 1: Keyword overlap (Jaccard)
        kw_score = self._jaccard(source_keywords, target_keywords)

        score = HomScore(
            source=source_label or str(source_keywords[:3]),
            target=target_label or str(target_keywords[:3]),
            keyword_score=kw_score,
        )

        # Pass 2: Mnēmē embedding similarity
        if self.use_mneme and source_keywords:
            query = " ".join(source_keywords[:5])
            emb_score = self._mneme_similarity(query, target_keywords)
            score.embedding_score = emb_score

        # Pass 3: LLM judgment (only for ambiguous cases)
        if self.use_llm and 0.2 <= score.combined_score <= 0.5:
            llm = self._llm_judge(source_keywords, target_keywords)
            score.llm_score = llm

        return score

    def batch_compute(
        self,
        source_keywords: list[str],
        targets: list[tuple[str, list[str]]],  # (label, keywords)
    ) -> list[HomScore]:
        """Compute Hom scores against multiple targets."""
        return [
            self.compute(
                source_keywords,
                target_kw,
                source_label=" ".join(source_keywords[:3]),
                target_label=label,
            )
            for label, target_kw in targets
        ]

    # --- Pass implementations ---

    def _jaccard(self, a: list[str], b: list[str]) -> float:
        """Pass 1: Jaccard coefficient between keyword sets."""
        set_a = {kw.lower().strip() for kw in a if kw.strip()}
        set_b = {kw.lower().strip() for kw in b if kw.strip()}

        if not set_a or not set_b:
            return 0.0

        # Also check substring containment for partial matches
        intersection = set_a & set_b
        # Add partial matches
        for wa in set_a:
            for wb in set_b:
                if wa in wb or wb in wa:
                    intersection.add(wa)

        union = set_a | set_b
        return len(intersection) / len(union) if union else 0.0

    def _mneme_similarity(self, query: str, target_keywords: list[str]) -> Optional[float]:
        """Pass 2: Use Mnēmē vector search to estimate semantic similarity."""
        try:
            # Search Mnēmē for the query
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    (
                        "import json, sys; "
                        "sys.path.insert(0, '.'); "
                        "from mekhane.mneme.search import search; "
                        f"results = search('{query}', k=5); "
                        "print(json.dumps([{'text': r.get('text','')[:100], 'score': r.get('score',0)} for r in results]))"
                    ),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.project_root),
            )
            if result.returncode == 0 and result.stdout.strip():
                hits = json.loads(result.stdout.strip())
                if hits:
                    # Check if any hit mentions target keywords
                    target_lower = {kw.lower() for kw in target_keywords}
                    max_relevance = 0.0
                    for hit in hits:
                        hit_text = hit.get("text", "").lower()
                        matches = sum(1 for kw in target_lower if kw in hit_text)
                        if matches > 0:
                            relevance = min(1.0, matches / max(1, len(target_lower)))
                            max_relevance = max(max_relevance, relevance)
                    return max_relevance
        except (subprocess.TimeoutExpired, OSError, json.JSONDecodeError):
            pass
        return None

    def _llm_judge(self, source: list[str], target: list[str]) -> Optional[float]:
        """Pass 3: LLM judgment for edge cases."""
        # Only triggered for ambiguous cases (score between 0.2 and 0.5)
        prompt = (
            f"以下の2つの概念群の関連性を0.0〜1.0で評価してください。\n"
            f"概念A: {', '.join(source[:5])}\n"
            f"概念B: {', '.join(target[:5])}\n"
            f"数値のみ返してください。"
        )
        try:
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f"from mekhane.ochema.cortex_client import CortexClient; "
                    f"c = CortexClient(); "
                    f"r = c.ask('''{prompt}''', model='gemini-2.0-flash'); "
                    f"print(r.text.strip())",
                ],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=str(self.project_root),
            )
            if result.returncode == 0:
                try:
                    return float(result.stdout.strip())
                except ValueError:
                    pass
        except (subprocess.TimeoutExpired, OSError):
            pass
        return None
