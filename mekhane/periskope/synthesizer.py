# PROOF: [S2/Mekhanē] <- mekhane/ A0->Implementation
# PURPOSE: Synthesize search results using multiple LLMs
"""
Multi-model synthesizer for Periskopē.

Synthesizes search results using multiple LLMs in parallel:
- Gemini (via Cortex API direct)
- Claude (via Language Server, extensible to parallel LS)

Detects divergence between models to identify uncertain claims.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from mekhane.periskope.models import (
    Citation,
    DivergenceReport,
    SearchResult,
    SynthesisResult,
    SynthModel,
    TaintLevel,
)

logger = logging.getLogger(__name__)

# Synthesis prompt template
_SYNTH_PROMPT = """You are a research synthesizer. Given the following search results
for the query "{query}", produce a comprehensive synthesis.

Requirements:
1. Synthesize the key findings across all sources
2. Cite specific sources using [Source N] notation
3. Note any contradictions between sources
4. Rate your confidence (0-100%) in the synthesis

Search Results:
{results_text}

Provide your synthesis in a structured format with sections:
## Key Findings
## Source Analysis
## Contradictions (if any)
## Confidence: X%
"""


class MultiModelSynthesizer:
    """Synthesize search results using multiple LLMs.

    Uses CortexClient (Gemini) as primary synthesizer.
    LS-based Claude synthesis is supported via the extensible
    synth_models configuration.

    Architecture:
        synth_models = [GEMINI_FLASH]  # Start with 1 model
        # Extensible to: [GEMINI_FLASH, CLAUDE_LS] for parallel
    """

    def __init__(
        self,
        synth_models: list[SynthModel] | None = None,
        cortex_model: str = "gemini-3-flash-preview",
        max_tokens: int = 4096,
    ) -> None:
        self.synth_models = synth_models or [SynthModel.GEMINI_FLASH]
        self.cortex_model = cortex_model
        self.max_tokens = max_tokens
        self._cortex = None

    def _get_cortex(self):
        """Lazy-load CortexClient."""
        if self._cortex is None:
            from mekhane.ochema.cortex_client import CortexClient
            self._cortex = CortexClient(
                model=self.cortex_model,
                max_tokens=self.max_tokens,
            )
        return self._cortex

    async def synthesize(
        self,
        query: str,
        search_results: list[SearchResult],
        system_instruction: str | None = None,
    ) -> list[SynthesisResult]:
        """Synthesize search results using configured models.

        Args:
            query: Original search query.
            search_results: Aggregated search results from all searchers.
            system_instruction: Optional system prompt override.

        Returns:
            List of SynthesisResult (one per model).
        """
        if not search_results:
            logger.warning("No search results to synthesize")
            return []

        results_text = self._format_results(search_results)
        prompt = _SYNTH_PROMPT.format(query=query, results_text=results_text)

        tasks = []
        for model in self.synth_models:
            if model in (SynthModel.GEMINI_FLASH, SynthModel.GEMINI_PRO):
                tasks.append(self._synth_gemini(prompt, model, system_instruction))
            elif model == SynthModel.CLAUDE_LS:
                tasks.append(self._synth_claude_ls(prompt, system_instruction))
            else:
                logger.warning("Unsupported synth model: %s", model)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        synth_results = []
        for r in results:
            if isinstance(r, SynthesisResult):
                synth_results.append(r)
            elif isinstance(r, Exception):
                logger.error("Synthesis failed: %s", r)

        return synth_results

    async def _synth_gemini(
        self,
        prompt: str,
        model: SynthModel,
        system_instruction: str | None,
    ) -> SynthesisResult:
        """Synthesize via Cortex (Gemini) API."""
        cortex = self._get_cortex()

        gemini_model = model.value  # e.g., "gemini-3-flash-preview"

        start = time.monotonic()
        response = await cortex.ask_async(
            message=prompt,
            model=gemini_model,
            system_instruction=system_instruction or "You are a thorough research analyst.",
            max_tokens=self.max_tokens,
        )
        elapsed = time.monotonic() - start

        # Extract citations from the response
        citations = self._extract_citations(response.text)

        # Extract confidence from response text
        confidence = self._extract_confidence(response.text)

        logger.info(
            "Gemini synthesis (%s): %d chars in %.1fs, confidence=%d%%",
            gemini_model, len(response.text), elapsed, int(confidence * 100),
        )

        return SynthesisResult(
            model=model,
            content=response.text,
            citations=citations,
            confidence=confidence,
            thinking=response.thinking or "",
            token_count=response.usage.get("total", 0) if hasattr(response, "usage") else 0,
        )

    async def _synth_claude_ls(
        self,
        prompt: str,
        system_instruction: str | None,
    ) -> SynthesisResult:
        """Synthesize via Language Server (Claude).

        Uses AntigravityClient to connect to the running LS.
        Falls back to error if LS is not running.
        """
        try:
            from mekhane.ochema.antigravity_client import AntigravityClient, LLMResponse

            # AntigravityClient.ask() is synchronous — wrap in thread
            def _call_ls() -> LLMResponse:
                client = AntigravityClient()
                return client.ask(
                    message=prompt,
                    model="MODEL_CLAUDE_4_5_SONNET_THINKING",
                    timeout=120.0,
                )

            start = time.monotonic()
            response = await asyncio.to_thread(_call_ls)
            elapsed = time.monotonic() - start

            citations = self._extract_citations(response.text)
            confidence = self._extract_confidence(response.text)

            logger.info(
                "Claude LS synthesis: %d chars in %.1fs, confidence=%d%%",
                len(response.text), elapsed, int(confidence * 100),
            )

            return SynthesisResult(
                model=SynthModel.CLAUDE_LS,
                content=response.text,
                citations=citations,
                confidence=confidence,
                thinking=response.thinking or "",
                token_count=response.token_usage.get("total_tokens", 0)
                if isinstance(response.token_usage, dict)
                else 0,
            )

        except Exception as e:
            logger.warning("Claude LS synthesis failed (LS may not be running): %s", e)
            raise RuntimeError(f"Claude LS unavailable: {e}") from e

    def detect_divergence(
        self,
        results: list[SynthesisResult],
    ) -> DivergenceReport:
        """Detect divergence between multiple model outputs.

        Compares outputs from different models to identify:
        - Points of agreement (consensus claims)
        - Points of disagreement (divergent claims)
        - Overall agreement score

        Args:
            results: List of synthesis results from different models.

        Returns:
            DivergenceReport with agreement analysis.
        """
        if len(results) < 2:
            return DivergenceReport(
                models_compared=[r.model for r in results],
                agreement_score=1.0,
                divergent_claims=[],
                consensus_claims=["Single model — no divergence detection possible"],
            )

        # Simple heuristic: compare confidence scores
        confidences = [r.confidence for r in results]
        avg_confidence = sum(confidences) / len(confidences)
        confidence_spread = max(confidences) - min(confidences)

        # Agreement score: inverse of confidence spread
        agreement = max(0.0, 1.0 - confidence_spread)

        return DivergenceReport(
            models_compared=[r.model for r in results],
            agreement_score=agreement,
            divergent_claims=[
                f"Confidence spread: {confidence_spread:.2f}"
            ] if confidence_spread > 0.2 else [],
            consensus_claims=[
                f"Average confidence: {avg_confidence:.2f}"
            ],
        )

    def _format_results(self, results: list[SearchResult]) -> str:
        """Format search results for the synthesis prompt."""
        lines = []
        for i, r in enumerate(results, 1):
            source_tag = f"[{r.source.value}]" if r.source else ""
            url_line = f"\n   URL: {r.url}" if r.url else ""
            lines.append(
                f"[Source {i}] {source_tag} {r.title}"
                f"{url_line}"
                f"\n   {r.content[:500]}"
            )
        return "\n\n".join(lines)

    def _extract_citations(self, text: str) -> list[Citation]:
        """Extract [Source N] citations from synthesis text."""
        import re

        citations = []
        # Find all [Source N] references
        refs = re.findall(r'\[Source\s+(\d+)\]', text)
        seen = set()
        for ref_num in refs:
            if ref_num not in seen:
                seen.add(ref_num)
                citations.append(Citation(
                    claim=f"Referenced as Source {ref_num}",
                    source_url="",
                    taint_level=TaintLevel.UNCHECKED,
                ))
        return citations

    def _extract_confidence(self, text: str) -> float:
        """Extract confidence percentage from synthesis text."""
        import re

        match = re.search(r'Confidence:\s*(\d+)%', text)
        if match:
            return min(1.0, int(match.group(1)) / 100.0)
        return 0.5  # Default moderate confidence
