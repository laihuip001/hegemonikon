# PROOF: [L2/Mekhane] <- mekhane/periskope/query_expander.py S2->Mekhane->query_expander
"""
Query expander for Periskopē.

W3: Expands queries by translating between Japanese and English,
enabling parallel bilingual search for broader result coverage.
Uses Cortex API (Gemini) for lightweight translation.
"""

from __future__ import annotations

import logging
import os
import re
import unicodedata

import httpx

logger = logging.getLogger(__name__)

# CJK Unicode ranges for Japanese detection
_CJK_RANGES = (
    ('\u3040', '\u309f'),  # Hiragana
    ('\u30a0', '\u30ff'),  # Katakana
    ('\u4e00', '\u9fff'),  # CJK Unified Ideographs
    ('\u3400', '\u4dbf'),  # CJK Extension A
)


def _is_japanese(text: str) -> bool:
    """Detect if text contains Japanese characters."""
    for char in text:
        for start, end in _CJK_RANGES:
            if start <= char <= end:
                return True
    return False


class QueryExpander:
    """Expand search queries via translation and synonym generation.

    Uses Cortex API (Gemini Flash) for fast, cost-effective translation.
    """

    def __init__(
        self,
        cortex_base_url: str = "http://localhost:8765",
        model: str = "gemini-2.0-flash",
        timeout: float = 15.0,
    ) -> None:
        self.cortex_base_url = cortex_base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def expand(self, query: str) -> list[str]:
        """Expand query via bilingual translation.

        Args:
            query: Original search query.

        Returns:
            List of queries (original + translated).
            If translation fails, returns only the original.
        """
        queries = [query]

        try:
            if _is_japanese(query):
                translated = await self._translate(query, "ja", "en")
            else:
                translated = await self._translate(query, "en", "ja")

            if translated and translated.strip() != query.strip():
                queries.append(translated.strip())
                logger.info("Query expanded: %r → %r", query, translated.strip())
        except Exception as e:
            logger.warning("Query expansion failed: %s", e)

        return queries

    async def _translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> str | None:
        """Translate text using Cortex API (Gemini Flash).

        Args:
            text: Text to translate.
            source_lang: Source language code (ja, en).
            target_lang: Target language code (ja, en).

        Returns:
            Translated text, or None on failure.
        """
        lang_names = {"ja": "Japanese", "en": "English"}
        prompt = (
            f"Translate the following {lang_names[source_lang]} search query "
            f"to {lang_names[target_lang]}. "
            f"Return ONLY the translated text, nothing else.\n\n"
            f"{text}"
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.cortex_base_url}/api/chat",
                    json={
                        "model": self.model,
                        "message": prompt,
                        "max_tokens": 256,
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Cortex API returns response in 'response' or 'text' field
                result = data.get("response") or data.get("text") or ""
                return result.strip() if result else None

        except Exception as e:
            logger.debug("Translation via Cortex failed: %s", e)
            return None
