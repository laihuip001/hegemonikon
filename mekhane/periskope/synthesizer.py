# PROOF: [L2/Search] <- mekhane/periskope/synthesizer.py A0→AutoFix
"""
Multi-model synthesizer for Periskopē.

Synthesizes search results using multiple LLMs in parallel:
- Gemini (via CortexClient.chat() — generateChat API)
- Claude (via CortexClient.chat() — generateChat API, LS 不要)

Detects divergence between models to identify uncertain claims.

Depth-level model routing:
  L1: Gemini Pro only
  L2: Gemini Pro + Claude Sonnet
  L3: Gemini Pro + Claude Opus
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

# Synthesis prompt template — structured output
_SYNTH_PROMPT = """You are a research synthesizer. Given the following search results
for the query "{query}", produce a comprehensive synthesis.

Requirements:
1. Synthesize the key findings across all sources
2. Cite specific sources using [Source N] notation
3. Note any contradictions between sources
4. Rate your confidence (0-100%) in the synthesis

Search Results:
{results_text}

Output your synthesis in EXACTLY this format:

## Key Findings
- [finding 1] [Source N]
- [finding 2] [Source N]
(list all key findings, each citing sources)

## Source Analysis
- [Source N]: [brief assessment of source quality/relevance]

## Contradictions
- [contradiction description] (between [Source X] and [Source Y])
(write "None identified" if no contradictions)

## Confidence: X%
(single integer 0-100)
"""

# Depth-level → model selection mapping
_DEPTH_MODELS: dict[int, list[SynthModel]] = {
    1: [SynthModel.GEMINI_PRO],
    2: [SynthModel.GEMINI_PRO, SynthModel.CLAUDE_SONNET],
    3: [SynthModel.GEMINI_PRO, SynthModel.CLAUDE_OPUS],
}


def models_for_depth(depth: int) -> list[SynthModel]:
    """Return synthesis models for the given depth level (1-3)."""
    return _DEPTH_MODELS.get(depth, _DEPTH_MODELS[2])


class MultiModelSynthesizer:
    """Synthesize search results using multiple LLMs.

    Uses CortexClient.chat() (generateChat API) for both Gemini and Claude.
    No Language Server dependency — all models accessed directly via Cortex.

    Depth-level routing:
        L1: Gemini Pro only (fast, single-model)
        L2: Gemini Pro + Claude Sonnet (standard dual-model)
        L3: Gemini Pro + Claude Opus (deep dual-model)
    """

    def __init__(
        self,
        synth_models: list[SynthModel] | None = None,
        gemini_model: str = "gemini-3-pro-preview",
        max_tokens: int = 4096,
    ) -> None:
        self.synth_models = synth_models or models_for_depth(2)
        self.gemini_model = gemini_model
        self.max_tokens = max_tokens
        self._cortex = None

    def _get_cortex(self):
        """Lazy-load CortexClient."""
        if self._cortex is None:
            from mekhane.ochema.cortex_client import CortexClient
            self._cortex = CortexClient(
                model=self.gemini_model,
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
                tasks.append(self._synth_via_cortex(prompt, model, system_instruction))
            elif model in (SynthModel.CLAUDE_SONNET, SynthModel.CLAUDE_OPUS):
                tasks.append(self._synth_via_cortex(prompt, model, system_instruction))
            elif model == SynthModel.CLAUDE_LS:
                # Deprecated: redirect to CLAUDE_SONNET via cortex
                logger.warning("CLAUDE_LS is deprecated, using CLAUDE_SONNET via Cortex")
                tasks.append(self._synth_via_cortex(
                    prompt, SynthModel.CLAUDE_SONNET, system_instruction,
                ))
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

    async def _synth_via_cortex(
        self,
        prompt: str,
        model: SynthModel,
        system_instruction: str | None,
    ) -> SynthesisResult:
        """Synthesize via CortexClient.chat() (generateChat API).

        Works for both Gemini and Claude models — unified pathway.
        """
        cortex = self._get_cortex()

        # model.value is the model_config_id (e.g. "gemini-3-pro-preview", "claude-sonnet-4-5")
        model_id = model.value

        # Prepend system instruction to the prompt if provided
        # (generateChat doesn't have a separate system_instruction field)
        full_prompt = prompt
        if system_instruction:
            full_prompt = f"System: {system_instruction}\n\n{prompt}"

        start = time.monotonic()

        # CortexClient.chat() is sync — run in thread pool
        response = await asyncio.to_thread(
            cortex.chat,
            message=full_prompt,
            model=model_id,
            timeout=120.0,
        )
        elapsed = time.monotonic() - start

        # Extract citations from the response
        citations = self._extract_citations(response.text)

        # Extract confidence from response text
        confidence = self._extract_confidence(response.text)

        logger.info(
            "Synthesis (%s): %d chars in %.1fs, confidence=%d%%",
            model_id, len(response.text), elapsed, int(confidence * 100),
        )

        return SynthesisResult(
            model=model,
            content=response.text,
            citations=citations,
            confidence=confidence,
            thinking=getattr(response, "thinking", "") or "",
            token_count=response.token_usage.get("total_tokens", 0)
            if isinstance(response.token_usage, dict)
            else 0,
        )

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
