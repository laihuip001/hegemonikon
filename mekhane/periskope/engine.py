# PROOF: [L2/Mekhanē] <- mekhane/periskope/
"""
PROOF: [L2/Mekhanē] This file is the core engine of Periskopē.
A0 (FEP) -> Active Inference requires deep information gathering -> Periskopē Engine.

# PURPOSE: Periskopē Deep Research Engine — Main Orchestrator
Coordinates search (SearXNG/Exa), synthesis (LLM), and verification (Citation).
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from mekhane.periskope.models import (
    PeriskopeConfig,
    PeriskopeReport,
    SearchResult,
    SearchSource,
    SynthesisResult,
    SynthModel,
)
from mekhane.periskope.searchers.searxng import SearXNGSearcher

logger = logging.getLogger(__name__)


class PeriskopeEngine:
    """Periskopē Deep Research Engine.

    Orchestrates the research process:
    1. Search: Gather information from multiple sources.
    2. Synthesize: Generate answers/reports using LLMs.
    3. Verify: Check citations and source reliability.
    """

    def __init__(self, config: PeriskopeConfig | None = None) -> None:
        """Initialize the engine with configuration.

        Args:
            config: Configuration for the research session.
        """
        self.config = config or PeriskopeConfig()
        self._searxng = SearXNGSearcher()
        # TODO: Initialize other searchers (Exa, Internal)
        # TODO: Initialize synthesizer (Ochema/Cortex)

    async def close(self) -> None:
        """Close all resources."""
        await self._searxng.close()

    async def search(self, query: str) -> list[SearchResult]:
        """Execute search across configured sources.

        Args:
            query: The search query string.

        Returns:
            A list of SearchResult objects from all sources.
        """
        tasks = []

        # Dispatch to SearXNG
        if SearchSource.SEARXNG in self.config.search_sources:
            tasks.append(
                self._searxng.search(
                    query,
                    max_results=self.config.max_results_per_source,
                )
            )

        # TODO: Dispatch to other sources (Exa, Gnosis, etc.)

        if not tasks:
            logger.warning("No search sources configured.")
            return []

        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        all_results: list[SearchResult] = []
        for res in results_list:
            if isinstance(res, list):
                all_results.extend(res)
            elif isinstance(res, Exception):
                logger.error(f"Search task failed: {res}")

        # Sort by relevance
        all_results.sort(key=lambda x: x.relevance, reverse=True)
        return all_results

    async def synthesize(
        self,
        query: str,
        results: list[SearchResult],
    ) -> list[SynthesisResult]:
        """Synthesize search results into a report.

        Args:
            query: The original research query.
            results: The search results to synthesize.

        Returns:
            A list of SynthesisResult objects (one per model).
        """
        # TODO: Implement actual LLM synthesis via Ochema/Cortex
        # For now, return a placeholder result

        logger.info(f"Synthesizing {len(results)} results for query: {query}")

        placeholder = SynthesisResult(
            model=self.config.synth_models[0] if self.config.synth_models else SynthModel.GEMINI_FLASH,
            content=f"Synthesis not implemented yet. Found {len(results)} results.",
            citations=[],
            confidence=0.0,
            thinking="Synthesis logic pending implementation (S3).",
        )
        return [placeholder]

    async def run(self, query: str | None = None) -> PeriskopeReport:
        """Execute the full research pipeline.

        Args:
            query: Optional query override. Uses config.query if None.

        Returns:
            The final PeriskopeReport.
        """
        start_time = time.time()
        active_query = query or self.config.query

        if not active_query:
            raise ValueError("No query provided in run() or config.")

        # 1. Search
        search_results = await self.search(active_query)

        # 2. Synthesize
        synthesis_results = await self.synthesize(active_query, search_results)

        # 3. Verify (TODO)
        citations = []
        for synth in synthesis_results:
            citations.extend(synth.citations)

        # TODO: Implement verification logic

        execution_time = time.time() - start_time

        report = PeriskopeReport(
            query=active_query,
            config=self.config,
            search_results=search_results,
            synthesis_results=synthesis_results,
            citations=citations,
            total_sources=len(search_results),
            execution_time_seconds=execution_time,
            report_markdown=synthesis_results[0].content if synthesis_results else "",
        )

        return report
