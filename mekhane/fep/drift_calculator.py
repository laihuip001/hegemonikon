#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/fep/ A0→Drift を計算可能にする→drift_calculatorが担う
"""
Drift Calculator — [0,1]-Enriched Category Hom Value Computation

Origin: G2 of /bou + @dig (2026-02-11)
Mathematical Basis: Drift ∈ [0,1] as Hom value in [0,1]-enriched category

Drift(source, compressed) = 1 - weighted_avg(max_sim(chunk_i, compressed_chunks))

Three use cases:
    /bye:  source=Session summary,  compressed=Handoff
    /boot: source=Handoff,          compressed=Boot report
    /eat:  source=Original paper,   compressed=Knowledge Item

Implementation: Character n-gram TF-IDF + cosine similarity
    - No dependency on MeCab/Janome (morphological analyzers)
    - Works with Japanese/English/Greek mixed text
    - Only requires numpy (already available)

Design symmetry:
    cone_builder:       WF outputs → Cone (C0-C3)
    adjunction_builder: boot + handoff → Adjunction (η, ε, drift)
    drift_calculator:   source + compressed → DriftResult (value, lost, preserved)
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# =============================================================================
# DriftResult — "what was lost" matters more than the number
# =============================================================================


# PURPOSE: の統一的インターフェースを実現する
@dataclass
class DriftResult:
    """Result of drift computation between source and compressed texts.

    Category-theoretic interpretation:
        value = 1 - Hom(source, compressed) in [0,1]-enriched category
        lost_chunks = kernel of G (forgetful functor)
        preserved_chunks = image of G
    """

    value: float  # Drift ∈ [0, 1]. 0 = perfect preservation, 1 = total loss
    method: str  # "tfidf" or "coverage"
    lost_chunks: List[str] = field(default_factory=list)
    preserved_chunks: List[str] = field(default_factory=list)
    chunk_scores: Dict[str, float] = field(default_factory=dict)  # chunk → similarity

    # PURPOSE: drift_calculator の preservation rate 処理を実行する
    @property
    def preservation_rate(self) -> float:
        """Hom value = 1 - drift. How much was preserved."""
        return 1.0 - self.value

    # PURPOSE: drift_calculator の lost count 処理を実行する
    @property
    def lost_count(self) -> int:
        return len(self.lost_chunks)

    # PURPOSE: drift_calculator の preserved count 処理を実行する
    @property
    def preserved_count(self) -> int:
        return len(self.preserved_chunks)


# =============================================================================
# Character n-gram TF-IDF (zero-dependency Japanese/English support)
# =============================================================================


def _normalize_text(text: str) -> str:
    """Normalize text for n-gram extraction.

    Removes markdown formatting, excessive whitespace, and normalizes case.
    """
    # Remove markdown headers, links, code blocks
    text = re.sub(r'```[\s\S]*?```', ' ', text)
    text = re.sub(r'`[^`]+`', ' ', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'#{1,6}\s+', '', text)
    text = re.sub(r'[*_~]{1,3}', '', text)
    # Remove YAML frontmatter
    text = re.sub(r'^---\n[\s\S]*?\n---\n', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()


def _char_ngrams(text: str, n: int = 3) -> List[str]:
    """Extract character n-grams from text.

    Character n-grams work across Japanese/English/Greek without
    morphological analysis. 2-grams capture kanji pairs and English
    suffixes; 3-grams capture longer patterns.
    """
    normalized = _normalize_text(text)
    if len(normalized) < n:
        return [normalized] if normalized else []
    return [normalized[i:i + n] for i in range(len(normalized) - n + 1)]


def _build_vocabulary(documents: List[str], ngram_sizes: Tuple[int, ...] = (2, 3)) -> List[str]:
    """Build vocabulary from all documents using character n-grams."""
    vocab_set: set = set()
    for doc in documents:
        for n in ngram_sizes:
            vocab_set.update(_char_ngrams(doc, n))
    # Sort for deterministic ordering
    return sorted(vocab_set)


def _tf_vector(text: str, vocabulary: List[str],
               ngram_sizes: Tuple[int, ...] = (2, 3)) -> List[float]:
    """Compute TF (term frequency) vector for a document."""
    counts: Counter = Counter()
    for n in ngram_sizes:
        counts.update(_char_ngrams(text, n))

    total = sum(counts.values()) or 1
    return [counts.get(term, 0) / total for term in vocabulary]


def _idf_weights(documents: List[str], vocabulary: List[str],
                 ngram_sizes: Tuple[int, ...] = (2, 3)) -> List[float]:
    """Compute IDF (inverse document frequency) weights."""
    n_docs = len(documents)
    if n_docs == 0:
        return [0.0] * len(vocabulary)

    # Count documents containing each term
    doc_counts = [0] * len(vocabulary)
    for doc in documents:
        doc_ngrams = set()
        for n in ngram_sizes:
            doc_ngrams.update(_char_ngrams(doc, n))
        for i, term in enumerate(vocabulary):
            if term in doc_ngrams:
                doc_counts[i] += 1

    # IDF = log(N / (1 + df)) + 1 (smoothed)
    return [math.log(n_docs / (1 + df)) + 1.0 for df in doc_counts]


def _tfidf_vector(text: str, vocabulary: List[str], idf: List[float],
                  ngram_sizes: Tuple[int, ...] = (2, 3)) -> List[float]:
    """Compute TF-IDF vector for a document."""
    tf = _tf_vector(text, vocabulary, ngram_sizes)
    return [t * i for t, i in zip(tf, idf)]


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors.

    Uses pure Python to avoid numpy import at module level.
    numpy is used only when available for performance.
    """
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# =============================================================================
# Text chunking
# =============================================================================


def _split_into_chunks(text: str, min_length: int = 50) -> List[str]:
    """Split text into meaningful chunks.

    Uses paragraph breaks (double newlines) as primary delimiter.
    Merges short chunks to avoid noise.
    """
    # Split on double newlines (paragraph boundaries)
    raw_chunks = re.split(r'\n\s*\n', text)

    # Filter and merge short chunks
    chunks: List[str] = []
    buffer = ""
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        if len(chunk) < min_length:
            buffer += " " + chunk
        else:
            if buffer:
                # Merge buffer with current chunk
                chunks.append((buffer + " " + chunk).strip())
                buffer = ""
            else:
                chunks.append(chunk)
    if buffer:
        chunks.append(buffer.strip())

    return [c for c in chunks if len(c) >= min_length // 2]


# =============================================================================
# Drift computation: TF-IDF method
# =============================================================================


# PURPOSE: drift を計算する
def compute_drift(
    source: str,
    compressed: str,
    *,
    method: str = "tfidf",
    threshold: float = 0.3,
    ngram_sizes: Tuple[int, ...] = (2, 3),
) -> DriftResult:
    """Compute drift between source text and its compressed version.

    Category-theoretic interpretation:
        Drift = 1 - Hom(source, compressed) in [0,1]-enriched category
        source = object in the original category
        compressed = G(F(source)) after forgetting functor G

    Args:
        source: Original text (session summary, paper, handoff)
        compressed: Compressed text (handoff, KI, boot report)
        method: "tfidf" (default) or "coverage"
        threshold: Similarity threshold for "preserved" classification
        ngram_sizes: Character n-gram sizes to use

    Returns:
        DriftResult with value, lost/preserved chunks, and per-chunk scores
    """
    if method == "coverage":
        return _compute_coverage_drift(source, compressed)
    return _compute_tfidf_drift(source, compressed, threshold, ngram_sizes)


def _compute_tfidf_drift(
    source: str,
    compressed: str,
    threshold: float,
    ngram_sizes: Tuple[int, ...],
) -> DriftResult:
    """TF-IDF cosine similarity based drift computation."""
    source_chunks = _split_into_chunks(source)
    compressed_chunks = _split_into_chunks(compressed)

    if not source_chunks:
        return DriftResult(value=0.0, method="tfidf")
    if not compressed_chunks:
        return DriftResult(
            value=1.0,
            method="tfidf",
            lost_chunks=source_chunks,
        )

    # Build vocabulary from all chunks
    all_docs = source_chunks + compressed_chunks
    vocabulary = _build_vocabulary(all_docs, ngram_sizes)

    if not vocabulary:
        return DriftResult(value=0.5, method="tfidf")

    # Compute IDF weights
    idf = _idf_weights(all_docs, vocabulary, ngram_sizes)

    # Compute TF-IDF vectors for compressed chunks
    compressed_vectors = [
        _tfidf_vector(chunk, vocabulary, idf, ngram_sizes)
        for chunk in compressed_chunks
    ]

    # For each source chunk, find max similarity with any compressed chunk
    chunk_scores: Dict[str, float] = {}
    lost: List[str] = []
    preserved: List[str] = []

    for src_chunk in source_chunks:
        src_vector = _tfidf_vector(src_chunk, vocabulary, idf, ngram_sizes)

        max_sim = max(
            _cosine_similarity(src_vector, comp_vec)
            for comp_vec in compressed_vectors
        )

        # Truncate chunk for display (first 80 chars)
        display = src_chunk[:80].replace('\n', ' ')
        if len(src_chunk) > 80:
            display += "..."
        chunk_scores[display] = round(max_sim, 3)

        if max_sim >= threshold:
            preserved.append(display)
        else:
            lost.append(display)

    # Drift = 1 - weighted average similarity
    total_sim = sum(chunk_scores.values())
    avg_sim = total_sim / len(chunk_scores) if chunk_scores else 0.0
    drift_value = round(1.0 - avg_sim, 3)

    return DriftResult(
        value=max(0.0, min(1.0, drift_value)),
        method="tfidf",
        lost_chunks=lost,
        preserved_chunks=preserved,
        chunk_scores=chunk_scores,
    )


# =============================================================================
# Drift computation: Coverage method (lightweight fallback)
# =============================================================================


def _compute_coverage_drift(source: str, compressed: str) -> DriftResult:
    """Keyword coverage based drift (lightweight).

    Extracts markdown headers and bold text as key concepts,
    then checks presence in compressed text.
    """
    # Extract key concepts from source
    source_headers = re.findall(r'^#{1,4}\s+(.+)$', source, re.MULTILINE)
    source_bold = re.findall(r'\*\*(.+?)\*\*', source)
    source_concepts = list(dict.fromkeys(source_headers + source_bold))

    if not source_concepts:
        # Fallback: use long words as concepts
        words = set(re.findall(r'\b\w{4,}\b', _normalize_text(source)))
        source_concepts = sorted(words)[:30]

    if not source_concepts:
        return DriftResult(value=0.5, method="coverage")

    compressed_lower = compressed.lower()
    lost: List[str] = []
    preserved: List[str] = []
    scores: Dict[str, float] = {}

    for concept in source_concepts:
        if concept.lower() in compressed_lower:
            preserved.append(concept)
            scores[concept] = 1.0
        else:
            lost.append(concept)
            scores[concept] = 0.0

    coverage = len(preserved) / len(source_concepts)

    return DriftResult(
        value=round(1.0 - coverage, 3),
        method="coverage",
        lost_chunks=lost,
        preserved_chunks=preserved,
        chunk_scores=scores,
    )


# =============================================================================
# Display (symmetric with describe_adjunction, describe_cone)
# =============================================================================


# PURPOSE: drift_calculator の describe drift 処理を実行する
def describe_drift(result: DriftResult) -> str:
    """Human-readable description of drift measurement.

    Symmetric with cone_builder.describe_cone() and
    adjunction_builder.describe_adjunction().
    """
    lines = [
        f"📐 Drift Measurement (method: {result.method})",
        f"  Drift value:  {result.value:.1%}",
        f"  Preservation: {result.preservation_rate:.1%}",
        f"  Preserved:    {result.preserved_count} chunks",
        f"  Lost:         {result.lost_count} chunks",
    ]

    # Drift level indicator
    if result.value > 0.5:
        lines.append("  🔴 High drift — significant information loss")
    elif result.value > 0.25:
        lines.append("  🟡 Moderate drift — some information lost")
    else:
        lines.append("  🟢 Low drift — good preservation")

    # Top 3 lost chunks
    if result.lost_chunks:
        lines.append("")
        lines.append("  Lost information:")
        for chunk in result.lost_chunks[:5]:
            lines.append(f"    ❌ {chunk}")

    # Top 3 preserved chunks
    if result.preserved_chunks:
        lines.append("")
        lines.append("  Preserved information:")
        for chunk in result.preserved_chunks[:5]:
            lines.append(f"    ✅ {chunk}")

    return "\n".join(lines)


# =============================================================================
# CLI entry point
# =============================================================================


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) < 3:
        print("Usage: python drift_calculator.py <source_file> <compressed_file>")
        print("Example: python drift_calculator.py session.md handoff.md")
        sys.exit(1)

    source_path = Path(sys.argv[1])
    compressed_path = Path(sys.argv[2])

    if not source_path.exists() or not compressed_path.exists():
        print(f"Error: file not found")
        sys.exit(1)

    source_text = source_path.read_text(encoding="utf-8")
    compressed_text = compressed_path.read_text(encoding="utf-8")

    result = compute_drift(source_text, compressed_text)
    print(describe_drift(result))
