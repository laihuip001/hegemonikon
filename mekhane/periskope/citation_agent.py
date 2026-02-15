"""
Citation verification agent for Periskopē.

Verifies claims against their source URLs by fetching content
and computing fuzzy similarity. Assigns BC-6 TAINT levels
automatically based on verification results.
"""

from __future__ import annotations

import asyncio
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
        ≥0.8 similarity → SOURCE (verified)
        ≥0.5 similarity → TAINT (partially supported)
        <0.5 similarity → FABRICATED (unsupported)
    """

    # Similarity thresholds for TAINT classification
    THRESHOLD_SOURCE = 0.6    # ≥ this → SOURCE
    THRESHOLD_TAINT = 0.3     # ≥ this → TAINT
    # < THRESHOLD_TAINT → FABRICATED

    def __init__(
        self,
        timeout: float = 15.0,
        max_content_length: int = 10000,
    ) -> None:
        self.timeout = timeout
        self.max_content_length = max_content_length

    async def verify_citations(
        self,
        citations: list[Citation],
        source_contents: dict[str, str] | None = None,
    ) -> list[Citation]:
        """Verify a list of citations.

        Args:
            citations: Citations to verify.
            source_contents: Pre-fetched content keyed by URL (optional).
                If provided, skips URL fetching for matching URLs.

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
        """Compute fuzzy similarity between claim and source content.

        Uses multiple strategies:
        1. Direct substring check (highest confidence)
        2. Sentence-level SequenceMatcher
        3. Keyword overlap ratio

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

        # Weighted combination
        return 0.6 * best_sentence_score + 0.4 * keyword_score

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

        Args:
            synthesis_text: The synthesized text with [Source N] references.
            search_results: Original search results for URL resolution.

        Returns:
            List of Citation objects ready for verification.
        """
        citations = []

        # Build source index
        source_urls: dict[int, str] = {}
        if search_results:
            for i, r in enumerate(search_results, 1):
                if hasattr(r, "url") and r.url:
                    source_urls[i] = r.url

        # Find sentences with [Source N] citations
        sentences = re.split(r'(?<=[.!?])\s+', synthesis_text)
        for sentence in sentences:
            refs = re.findall(r'\[Source\s+(\d+)\]', sentence)
            if not refs:
                continue

            # Clean the sentence (remove [Source N] markers)
            clean = re.sub(r'\s*\[Source\s+\d+\]\s*', ' ', sentence).strip()
            if len(clean) < 20:
                continue

            for ref_num in refs:
                idx = int(ref_num)
                url = source_urls.get(idx, "")
                citations.append(Citation(
                    claim=clean,
                    source_url=url,
                    taint_level=TaintLevel.UNCHECKED,
                ))

        return citations
