# PROOF: [L2/periskope] <- mekhane/periskope/
"""
Citation verification agent for Periskopē.

Verifies claims against their source URLs by fetching content
and computing fuzzy similarity. Assigns BC-6 TAINT levels
automatically based on verification results.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from difflib import SequenceMatcher
from typing import Any

from mekhane.periskope.models import Citation, TaintLevel

logger = logging.getLogger(__name__)


class CitationAgent:
    """Verify citations by matching claims against source content.

    Architecture:
        1. Extract claims and their source URLs from synthesis text
        2. Fetch source content (via httpx or fallback)
        3. Fuzzy match claim against source content
        4. Assign TaintLevel based on similarity score

    BC-6 TAINT Mapping:
        ≥0.65 similarity → SOURCE (verified)
        ≥0.40 similarity → TAINT (partially supported)
        <0.40 similarity → FABRICATED (unsupported)
    """

    # Default similarity thresholds for TAINT classification
    THRESHOLD_SOURCE = 0.65   # ≥ this → SOURCE
    THRESHOLD_TAINT = 0.40    # ≥ this → TAINT
    # < THRESHOLD_TAINT → FABRICATED

    def __init__(
        self,
        timeout: float = 15.0,
        max_content_length: int = 10000,
        threshold_source: float | None = None,
        threshold_taint: float | None = None,
    ) -> None:
        self.timeout = timeout
        self.max_content_length = max_content_length
        self._embedder = None
        if threshold_source is not None:
            self.THRESHOLD_SOURCE = threshold_source
        if threshold_taint is not None:
            self.THRESHOLD_TAINT = threshold_taint
        # F8: embedding cache (SHA256[:16] → vector)
        self._embed_cache: dict[str, list[float]] = {}

    async def verify_citations(
        self,
        citations: list[Citation],
        source_contents: dict[str, str] | None = None,
        verify_depth: int = 1,
    ) -> list[Citation]:
        """Verify a list of citations.

        Args:
            citations: Citations to verify.
            source_contents: Pre-fetched content keyed by URL (optional).
                If provided, skips URL fetching for matching URLs.
            verify_depth: 1 = direct verification, 2 = 2-hop chain verification (F13).

        Returns:
            Updated citations with taint_level, similarity, and verification_note.
        """
        if source_contents is None:
            source_contents = {}

        tasks = [
            self._verify_one(c, source_contents)
            for c in citations
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        verified = []
        for i, result in enumerate(results):
            if isinstance(result, Citation):
                verified.append(result)
            elif isinstance(result, Exception):
                logger.error("Citation verification failed: %s", result)
                c = citations[i]
                c.taint_level = TaintLevel.UNCHECKED
                c.verification_note = f"Verification error: {result}"
                verified.append(c)
            else:
                verified.append(citations[i])

        # Summary log
        levels = [c.taint_level for c in verified]
        logger.info(
            "Verified %d citations: %d SOURCE, %d TAINT, %d FABRICATED, %d UNCHECKED",
            len(verified),
            levels.count(TaintLevel.SOURCE),
            levels.count(TaintLevel.TAINT),
            levels.count(TaintLevel.FABRICATED),
            levels.count(TaintLevel.UNCHECKED),
        )

        # F13: 2-hop chain verification
        if verify_depth >= 2:
            verified = await self._verify_chain(verified, source_contents)

        return verified

    async def _verify_one(
        self,
        citation: Citation,
        source_contents: dict[str, str],
    ) -> Citation:
        """Verify a single citation."""
        if not citation.claim:
            citation.taint_level = TaintLevel.UNCHECKED
            citation.verification_note = "No claim to verify"
            return citation

        if not citation.source_url:
            citation.taint_level = TaintLevel.TAINT
            citation.verification_note = "No source URL — cannot verify"
            return citation

        # Get source content
        content = source_contents.get(citation.source_url)
        if content is None:
            content = await self._fetch_url(citation.source_url)
            if content:
                source_contents[citation.source_url] = content

        if not content:
            citation.taint_level = TaintLevel.TAINT
            citation.verification_note = "Could not fetch source content"
            return citation

        # Compute similarity
        similarity = self._compute_similarity(citation.claim, content)
        citation.similarity = similarity

        # Classify
        if similarity >= self.THRESHOLD_SOURCE:
            citation.taint_level = TaintLevel.SOURCE
            citation.verification_note = f"Verified: {similarity:.1%} match"
        elif similarity >= self.THRESHOLD_TAINT:
            citation.taint_level = TaintLevel.TAINT
            citation.verification_note = f"Partial match: {similarity:.1%}"
        else:
            citation.taint_level = TaintLevel.FABRICATED
            citation.verification_note = f"Unsupported: {similarity:.1%} match"

        return citation

    def _compute_similarity(self, claim: str, content: str) -> float:
        """Compute similarity between claim and source content.

        Uses multiple strategies (best score wins):
        1. Direct substring check (highest confidence)
        2. Sentence-level SequenceMatcher
        3. Keyword overlap ratio
        4. Semantic embedding similarity (BGE-M3 cosine)

        Returns:
            Similarity score between 0.0 and 1.0.
        """
        claim_lower = claim.lower().strip()
        content_lower = content.lower()

        # Strategy 1: Direct substring
        if claim_lower in content_lower:
            return 1.0

        # Strategy 2: Best sentence match
        content_truncated = content_lower[:self.max_content_length]
        sentences = re.split(r'[.!?\n]+', content_truncated)
        best_sentence_score = 0.0
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            score = SequenceMatcher(None, claim_lower, sentence).ratio()
            best_sentence_score = max(best_sentence_score, score)

        # Strategy 3: Keyword overlap
        claim_words = set(re.findall(r'\w+', claim_lower))
        content_words = set(re.findall(r'\w+', content_truncated))
        if claim_words:
            keyword_score = len(claim_words & content_words) / len(claim_words)
        else:
            keyword_score = 0.0

        # Lexical score (original weighted combination)
        lexical_score = 0.6 * best_sentence_score + 0.4 * keyword_score

        # Strategy 4: Semantic embedding similarity (BGE-M3)
        semantic_score = self._compute_semantic_similarity(claim, content_truncated)

        if semantic_score is not None:
            # Take best of lexical and semantic — LLM paraphrasing
            # is caught by semantic even when lexical fails
            return max(lexical_score, semantic_score)

        return lexical_score

    def _compute_semantic_similarity(
        self, claim: str, content: str,
    ) -> float | None:
        """Compute cosine similarity via BGE-M3 embeddings.

        Splits content into chunks, embeds claim + chunks,
        and returns max cosine similarity.
        Uses hash-based cache to avoid re-embedding identical text.

        Returns None if embedder is unavailable.
        """
        try:
            from mekhane.anamnesis.index import Embedder

            embedder = self._get_embedder()

            claim_vec = self._cached_embed(embedder, claim)

            # Split content into sentences for granular matching
            sentences = re.split(r'[.!?\n]+', content)
            chunks = [s.strip() for s in sentences if len(s.strip()) >= 20]

            if not chunks:
                return None

            # Embed chunks with cache
            chunk_vecs = [self._cached_embed(embedder, c) for c in chunks]

            # Cosine similarity = dot product (embeddings are L2-normalized)
            best = 0.0
            for vec in chunk_vecs:
                dot = sum(a * b for a, b in zip(claim_vec, vec))
                best = max(best, dot)

            # Normalize to [0, 1] range (cosine can be negative)
            return max(0.0, min(1.0, best))

        except Exception as e:
            logger.debug("Semantic similarity unavailable: %s", e)
            return None

    def _cached_embed(self, embedder, text: str) -> list[float]:
        """Embed text with hash-based caching."""
        key = hashlib.sha256(text.encode()).hexdigest()[:16]
        if key not in self._embed_cache:
            self._embed_cache[key] = embedder.embed(text)
        return self._embed_cache[key]

    async def _verify_chain(
        self,
        citations: list[Citation],
        source_contents: dict[str, str],
    ) -> list[Citation]:
        """F13: 2-hop chain verification.

        For TAINT citations, look for referenced URLs in the source content,
        fetch those 2nd-level sources, and re-verify the claim.
        If a 2nd-level source confirms the claim, upgrade to SOURCE.
        """
        _URL_PATTERN = re.compile(r'https?://[^\s\)\]>"]+')

        upgraded = 0
        for citation in citations:
            if citation.taint_level != TaintLevel.TAINT:
                continue

            content = source_contents.get(citation.source_url, "")
            if not content:
                continue

            # Extract URLs from source content
            ref_urls = _URL_PATTERN.findall(content)
            if not ref_urls:
                continue

            # Try up to 3 referenced URLs
            for ref_url in ref_urls[:3]:
                ref_content = source_contents.get(ref_url)
                if ref_content is None:
                    ref_content = await self._fetch_url(ref_url)
                    if ref_content:
                        source_contents[ref_url] = ref_content

                if not ref_content:
                    continue

                sim = self._compute_similarity(citation.claim, ref_content)
                if sim >= self.THRESHOLD_SOURCE:
                    citation.taint_level = TaintLevel.SOURCE
                    citation.similarity = max(citation.similarity or 0, sim)
                    citation.verification_note = (
                        f"2-hop verified via {ref_url[:60]} (sim={sim:.2f})"
                    )
                    upgraded += 1
                    break

        if upgraded:
            logger.info("F13: 2-hop chain upgraded %d citations to SOURCE", upgraded)

        return citations

    def _get_embedder(self):
        """Lazy-load embedder singleton."""
        if not hasattr(self, '_embedder') or self._embedder is None:
            from mekhane.anamnesis.index import Embedder
            self._embedder = Embedder()
        return self._embedder

    async def _fetch_url(self, url: str) -> str:
        """Fetch URL content as text."""
        if not url or url.startswith("file://"):
            # Local file
            path = url.replace("file://", "") if url.startswith("file://") else ""
            if path:
                try:
                    from pathlib import Path
                    return Path(path).read_text(encoding="utf-8", errors="replace")[
                        :self.max_content_length
                    ]
                except Exception:
                    return ""
            return ""

        try:
            import httpx

            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                text = response.text[:self.max_content_length]
                return text
        except Exception as e:
            logger.debug("Failed to fetch %s: %s", url, e)
            return ""

    def extract_claims_from_synthesis(
        self,
        synthesis_text: str,
        search_results: list | None = None,
    ) -> list[Citation]:
        """Extract verifiable claims from synthesis text.

        Parses [Source N] references and maps them to search result URLs.
        Improved claim extraction:
        - Splits at sentence boundaries
        - Only extracts sentences containing [Source N] citations
        - Removes modifiers/connectives for cleaner claims
        - Splits long claims (>200 chars) at clause boundaries
        - Filters out claims <20 chars

        Args:
            synthesis_text: The synthesized text with [Source N] references.
            search_results: Original search results for URL resolution.

        Returns:
            List of Citation objects ready for verification.
        """
        citations = []

        # Build source index
        source_urls: dict[int, str] = {}
        source_titles: dict[int, str] = {}
        if search_results:
            for i, r in enumerate(search_results, 1):
                if hasattr(r, "url") and r.url:
                    source_urls[i] = r.url
                if hasattr(r, "title") and r.title:
                    source_titles[i] = r.title

        # Find sentences with [Source N] citations
        # Fix 3: Remove meta-sections that are not verifiable claims
        clean_text = re.sub(
            r'## (?:Source Analysis|Contradictions|Confidence).*?(?=## |\Z)',
            '', synthesis_text, flags=re.DOTALL,
        )
        sentences = re.split(r'(?<=[.!?。！？])\s+', clean_text)
        for sentence in sentences:
            refs = re.findall(r'\[Source\s+(\d+)\]', sentence)
            if not refs:
                continue

            # Clean the sentence (remove [Source N] markers and leading connectives)
            clean = re.sub(r'\s*\[Source\s+\d+\]\s*', ' ', sentence).strip()
            # Remove leading connectives/modifiers
            clean = re.sub(
                r'^(However|Moreover|Furthermore|Additionally|In contrast|'
                r'Similarly|Specifically|In particular|For example|'
                r'According to|Based on|As noted|In summary|'
                r'しかし|また|さらに|特に|具体的には|例えば|'
                r'一方で|それに加えて|結果として)[,、]\s*',
                '', clean, flags=re.IGNORECASE,
            )
            clean = clean.strip()

            if len(clean) < 20:
                continue

            # Split long claims at clause boundaries
            claims = self._split_long_claim(clean)

            for claim_text in claims:
                if len(claim_text) < 20:
                    continue
                for ref_num in refs:
                    idx = int(ref_num)
                    url = source_urls.get(idx, "")
                    title = source_titles.get(idx, "")
                    citations.append(Citation(
                        claim=claim_text,
                        source_url=url,
                        source_title=title,
                        taint_level=TaintLevel.UNCHECKED,
                    ))

        return citations

    @staticmethod
    def _split_long_claim(text: str, max_len: int = 200) -> list[str]:
        """Split long claims at clause boundaries.

        Keeps claims under max_len by splitting at semicolons, commas,
        or conjunctions. Returns original if already short enough.
        """
        if len(text) <= max_len:
            return [text]

        # Try splitting at semicolons first
        parts = re.split(r';\s*', text)
        if len(parts) > 1:
            return [p.strip() for p in parts if len(p.strip()) >= 20]

        # Try splitting at clause-level conjunctions
        parts = re.split(
            r'(?:,\s*(?:and|but|while|whereas|which|that)\s+|'
            r'、(?:そして|しかし|ただし|一方))',
            text,
        )
        if len(parts) > 1:
            return [p.strip() for p in parts if len(p.strip()) >= 20]

        # Can't split meaningfully — return as-is
        return [text]

