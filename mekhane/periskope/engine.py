"""
Periskopē Deep Research Engine — Orchestrator.

Coordinates the full deep research pipeline:
  Phase 1: Parallel multi-source search
  Phase 2: Multi-model synthesis (Cortex/LS)
  Phase 3: Citation verification (BC-6 TAINT)
  Phase 4: Report generation

Usage:
    engine = PeriskopeEngine()
    report = await engine.research("Free Energy Principle")
    print(report.markdown())
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from mekhane.periskope.models import (
    SearchResult,
    SearchSource,
    SynthesisResult,
    SynthModel,
    Citation,
    TaintLevel,
    DivergenceReport,
)
from mekhane.periskope.searchers.searxng import SearXNGSearcher
from mekhane.periskope.searchers.exa_searcher import ExaSearcher
from mekhane.periskope.searchers.internal_searcher import (
    GnosisSearcher,
    SophiaSearcher,
    KairosSearcher,
)
from mekhane.periskope.synthesizer import MultiModelSynthesizer
from mekhane.periskope.citation_agent import CitationAgent

logger = logging.getLogger(__name__)


@dataclass
class ResearchReport:
    """Complete research report from Periskopē."""

    query: str
    search_results: list[SearchResult] = field(default_factory=list)
    synthesis: list[SynthesisResult] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    divergence: DivergenceReport | None = None
    elapsed_seconds: float = 0.0
    source_counts: dict[str, int] = field(default_factory=dict)

    def markdown(self) -> str:
        """Generate a Markdown report."""
        lines = [
            f"# Periskopē Research Report",
            f"",
            f"> **Query**: {self.query}",
            f"> **Time**: {self.elapsed_seconds:.1f}s",
            f"> **Sources**: {len(self.search_results)} results from {len(self.source_counts)} engines",
            f"",
        ]

        # Source breakdown
        lines.append("## Sources")
        lines.append("")
        lines.append("| Engine | Results |")
        lines.append("|:-------|--------:|")
        for source, count in sorted(self.source_counts.items()):
            lines.append(f"| {source} | {count} |")
        lines.append("")

        # Synthesis
        if self.synthesis:
            lines.append("## Synthesis")
            lines.append("")
            for s in self.synthesis:
                lines.append(f"### {s.model.value} (Confidence: {s.confidence:.0%})")
                lines.append("")
                lines.append(s.content)
                lines.append("")

        # Divergence
        if self.divergence and len(self.divergence.models_compared) > 1:
            lines.append("## Divergence Analysis")
            lines.append("")
            lines.append(f"- Agreement Score: {self.divergence.agreement_score:.2f}")
            if self.divergence.consensus_claims:
                lines.append(f"- Consensus: {'; '.join(self.divergence.consensus_claims)}")
            if self.divergence.divergent_claims:
                lines.append(f"- Divergence: {'; '.join(self.divergence.divergent_claims)}")
            lines.append("")

        # Citations
        if self.citations:
            verified = [c for c in self.citations if c.taint_level != TaintLevel.UNCHECKED]
            if verified:
                lines.append("## Citation Verification")
                lines.append("")
                lines.append("| Claim | Level | Score | Note |")
                lines.append("|:------|:------|------:|:-----|")
                for c in verified[:20]:  # Limit display
                    claim_short = c.claim[:60] + "..." if len(c.claim) > 60 else c.claim
                    score = f"{c.similarity:.0%}" if c.similarity is not None else "—"
                    lines.append(
                        f"| {claim_short} | {c.taint_level.value} | {score} | {c.verification_note or ''} |"
                    )
                lines.append("")

        return "\n".join(lines)


class PeriskopeEngine:
    """Orchestrate the full Periskopē deep research pipeline.

    Configurable searchers and synthesis models allow flexible
    composition for different research needs:

    - Quick: SearXNG only + Gemini Flash
    - Standard: SearXNG + Exa + Gnōsis + Gemini Flash
    - Deep: All searchers + multi-model + citation verification
    """

    def __init__(
        self,
        searxng_url: str = "http://localhost:8888",
        synth_models: list[SynthModel] | None = None,
        max_results_per_source: int = 10,
        verify_citations: bool = True,
    ) -> None:
        self.max_results = max_results_per_source
        self.verify_citations = verify_citations

        # Searchers
        self.searxng = SearXNGSearcher(base_url=searxng_url)
        self.exa = ExaSearcher()
        self.gnosis = GnosisSearcher()
        self.sophia = SophiaSearcher()
        self.kairos = KairosSearcher()

        # Synthesizer
        self.synthesizer = MultiModelSynthesizer(
            synth_models=synth_models or [SynthModel.GEMINI_FLASH],
        )

        # Citation Agent
        self.citation_agent = CitationAgent()

    async def research(
        self,
        query: str,
        sources: list[str] | None = None,
    ) -> ResearchReport:
        """Execute the full research pipeline.

        Args:
            query: Research query.
            sources: List of source names to use. If None, uses all.
                Valid: "searxng", "exa", "gnosis", "sophia", "kairos"

        Returns:
            ResearchReport with all phases completed.
        """
        start = time.monotonic()
        enabled = set(sources or ["searxng", "exa", "gnosis", "sophia", "kairos"])

        # Phase 1: Parallel search
        logger.info("Phase 1: Parallel search for %r (sources: %s)", query, enabled)
        search_results, source_counts = await self._phase_search(query, enabled)

        if not search_results:
            logger.warning("No search results found for %r", query)
            return ResearchReport(
                query=query,
                elapsed_seconds=time.monotonic() - start,
                source_counts=source_counts,
            )

        # Phase 2: Multi-model synthesis
        logger.info("Phase 2: Multi-model synthesis (%d results)", len(search_results))
        synthesis = await self.synthesizer.synthesize(query, search_results)
        divergence = self.synthesizer.detect_divergence(synthesis)

        # Phase 3: Citation verification
        citations = []
        if self.verify_citations and synthesis:
            logger.info("Phase 3: Citation verification")
            for synth_result in synthesis:
                extracted = self.citation_agent.extract_claims_from_synthesis(
                    synth_result.content, search_results,
                )
                # Pre-populate source contents from search results
                source_contents = {}
                for sr in search_results:
                    if sr.url and sr.content:
                        source_contents[sr.url] = sr.content
                verified = await self.citation_agent.verify_citations(
                    extracted, source_contents,
                )
                citations.extend(verified)

        elapsed = time.monotonic() - start
        logger.info("Research complete in %.1fs", elapsed)

        return ResearchReport(
            query=query,
            search_results=search_results,
            synthesis=synthesis,
            citations=citations,
            divergence=divergence,
            elapsed_seconds=elapsed,
            source_counts=source_counts,
        )

    async def _phase_search(
        self,
        query: str,
        enabled: set[str],
    ) -> tuple[list[SearchResult], dict[str, int]]:
        """Phase 1: Execute parallel searches."""
        tasks = {}

        if "searxng" in enabled:
            tasks["searxng"] = self.searxng.search(query, max_results=self.max_results)
        if "exa" in enabled:
            tasks["exa"] = self.exa.search(query, max_results=self.max_results)
        if "gnosis" in enabled:
            tasks["gnosis"] = self.gnosis.search(query, max_results=self.max_results)
        if "sophia" in enabled:
            tasks["sophia"] = self.sophia.search(query, max_results=self.max_results)
        if "kairos" in enabled:
            tasks["kairos"] = self.kairos.search(query, max_results=self.max_results)

        all_results: list[SearchResult] = []
        source_counts: dict[str, int] = {}

        if not tasks:
            return all_results, source_counts

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        for name, result in zip(tasks.keys(), results):
            if isinstance(result, list):
                all_results.extend(result)
                source_counts[name] = len(result)
                logger.info("  %s: %d results", name, len(result))
            elif isinstance(result, Exception):
                logger.error("  %s: FAILED — %s", name, result)
                source_counts[name] = 0

        # Sort by relevance (descending)
        all_results.sort(key=lambda r: r.relevance, reverse=True)

        return all_results, source_counts
