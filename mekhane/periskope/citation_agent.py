# PURPOSE: Verifies the authenticity of citations by checking claim similarity against source content.
# PROOF: S4 (Schema/Praxis) <- mekhane/periskope/PROOF.md

from difflib import SequenceMatcher
import re
from typing import List

from .models import Citation, TaintLevel


class CitationAgent:
    """
    Verifies citations against source content to detect hallucinations.
    Implements BC-6 TAINT classification logic.
    """

    def verify(self, citation: Citation, content: str) -> Citation:
        """
        Verifies if the citation's claim is supported by the source content.
        Updates the citation's taint_level and similarity score.

        Args:
            citation: The citation to verify.
            content: The full text content of the source.

        Returns:
            The verified citation with updated taint_level and similarity.
        """
        if not content:
            citation.taint_level = TaintLevel.UNCHECKED
            citation.similarity = 0.0
            return citation

        sentences = self._split_sentences(content)
        max_similarity = 0.0

        # Check against each sentence in the content to find the best match
        for sentence in sentences:
            similarity = self._calculate_similarity(citation.claim, sentence)
            if similarity > max_similarity:
                max_similarity = similarity

        citation.similarity = max_similarity

        if max_similarity > 0.8:
            citation.taint_level = TaintLevel.SOURCE
        elif max_similarity > 0.5:
            citation.taint_level = TaintLevel.TAINT
        else:
            citation.taint_level = TaintLevel.FABRICATED

        return citation

    def _split_sentences(self, content: str) -> List[str]:
        """Splits content into sentences for granular comparison."""
        # Simple split by punctuation followed by space or newline
        # Use lookbehind to keep the delimiter if needed, but for now simple split is fine
        return [s.strip() for s in re.split(r'[.!?]\s+', content) if s.strip()]

    def _calculate_similarity(self, claim: str, source_text: str) -> float:
        """Calculates similarity ratio between claim and source text."""
        if not claim or not source_text:
            return 0.0

        # Normalize for comparison (ignore trailing punctuation)
        claim_norm = claim.strip().rstrip('.!?')
        source_norm = source_text.strip().rstrip('.!?')

        # If normalized claim matches or is contained, perfect match
        if claim_norm == source_norm or claim_norm in source_norm:
            return 1.0

        return SequenceMatcher(None, claim, source_text).ratio()
