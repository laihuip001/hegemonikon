# PROOF: [L2/Mekhanē] <- mekhane/periskope/PROOF.md S2->Periskopē->engine.py
# PURPOSE: Periskopē Research Engine implementation.

from __future__ import annotations

import asyncio
import logging
import time
from typing import List

from mekhane.periskope.models import (
    Citation,
    PeriskopeConfig,
    PeriskopeReport,
    SearchResult,
    SearchSource,
    SynthesisResult,
)
from mekhane.periskope.searchers.exa_searcher import ExaSearcher
from mekhane.periskope.searchers.internal_searcher import (
    GnosisSearcher,
    KairosSearcher,
    SophiaSearcher,
)
from mekhane.periskope.searchers.searxng import SearXNGSearcher

logger = logging.getLogger(__name__)


class PeriskopeEngine:
    """Core engine for Periskopē research sessions.

    Orchestrates the research pipeline:
    1. Search (Parallel execution across multiple sources)
    2. Synthesis (Multi-model reasoning and answer generation)
    3. Verification (Citation checking and TAINT analysis)
    """

    def __init__(self) -> None:
        self.searxng = SearXNGSearcher()
        self.exa = ExaSearcher()
        self.gnosis = GnosisSearcher()
        self.sophia = SophiaSearcher()
        self.kairos = KairosSearcher()

    async def run(self, config: PeriskopeConfig) -> PeriskopeReport:
        """Execute a full research session based on configuration."""
        start_time = time.time()
        logger.info("Starting Periskopē session for query: %r", config.query)

        # 1. Search Phase
        search_results = await self._execute_search(config)

        # 2. Synthesis Phase (Placeholder for now as per S3)
        synthesis_results: List[SynthesisResult] = []
        # TODO: Implement synthesis logic when S3 is started.

        # 3. Verification Phase (Placeholder)
        citations: List[Citation] = []
        # TODO: Implement citation verification when S4 is started.

        # 4. Report Generation
        execution_time = time.time() - start_time
        report = PeriskopeReport(
            query=config.query,
            config=config,
            search_results=search_results,
            synthesis_results=synthesis_results,
            citations=citations,
            total_sources=len(search_results),
            execution_time_seconds=execution_time,
        )

        logger.info(
            "Periskopē session completed in %.2fs. Sources: %d",
            execution_time,
            len(search_results),
        )
        return report

    async def _execute_search(self, config: PeriskopeConfig) -> List[SearchResult]:
        """Execute search across all configured sources in parallel."""
        tasks = []

        # SearXNG
        if SearchSource.SEARXNG in config.search_sources:
            tasks.append(
                self.searxng.search(
                    query=config.query,
                    max_results=config.max_results_per_source,
                )
            )

        # Exa
        if SearchSource.EXA in config.search_sources:
            tasks.append(
                self.exa.search(
                    query=config.query,
                    max_results=config.max_results_per_source,
                )
            )

        # Gnosis
        if SearchSource.GNOSIS in config.search_sources:
            tasks.append(
                self.gnosis.search(
                    query=config.query,
                    max_results=config.max_results_per_source,
                )
            )

        # Sophia
        if SearchSource.SOPHIA in config.search_sources:
            tasks.append(
                self.sophia.search(
                    query=config.query,
                    max_results=config.max_results_per_source,
                )
            )

        # Kairos
        if SearchSource.KAIROS in config.search_sources:
            tasks.append(
                self.kairos.search(
                    query=config.query,
                    max_results=config.max_results_per_source,
                )
            )

        # Execute all search tasks
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)

        all_results: List[SearchResult] = []
        for res in results_lists:
            if isinstance(res, list):
                all_results.extend(res)
            elif isinstance(res, Exception):
                logger.error("Search task failed: %s", res)

        # Deduplicate by URL (if present)
        unique_results = []
        seen_urls = set()
        for r in all_results:
            if r.url and r.url in seen_urls:
                continue
            if r.url:
                seen_urls.add(r.url)
            unique_results.append(r)

        # Sort by relevance
        unique_results.sort(key=lambda x: x.relevance, reverse=True)

        return unique_results

    async def close(self) -> None:
        """Close any open resources."""
        await self.searxng.close()
