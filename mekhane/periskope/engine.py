# PROOF: [L2/Mekhane] <- mekhane/periskope/ A0→Implementation→engine.py
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
from datetime import datetime
from pathlib import Path
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

from mekhane.periskope.searchers.brave_searcher import BraveSearcher
from mekhane.periskope.searchers.tavily_searcher import TavilySearcher
from mekhane.periskope.searchers.semantic_scholar_searcher import SemanticScholarSearcher
from mekhane.periskope.searchers.internal_searcher import (
    GnosisSearcher,
    SophiaSearcher,
    KairosSearcher,
)
from mekhane.periskope.synthesizer import MultiModelSynthesizer
from mekhane.periskope.citation_agent import CitationAgent
from mekhane.periskope.query_expander import QueryExpander
from mekhane.periskope.page_fetcher import PageFetcher, INTERNAL_SOURCES

logger = logging.getLogger(__name__)


async def _llm_ask(prompt: str, model: str = "gemini-2.0-flash", max_tokens: int = 256) -> str:
    """Lightweight LLM call via OchemaService for internal pipeline steps.

    Used by W6 (refinement queries) and W7 (URL selection).
    Falls back to empty string on failure.
    """
    try:
        from mekhane.ochema.service import OchemaService
        svc = OchemaService.get()
        response = await svc.ask_async(
            prompt, model=model, max_tokens=max_tokens, timeout=15.0,
        )
        return response.text
    except Exception as e:
        logger.warning("_llm_ask failed: %s", e)
        return ""


async def _phi1_blind_spot_analysis(
    query: str,
    context: str = "",
) -> list[str]:
    """Φ1: 無知のリマインド — Query blind spot analysis.

    Analyzes the query for implicit assumptions, missing perspectives,
    and alternative framings. Returns supplementary queries that cover
    the identified blind spots.

    This runs automatically inside the pipeline (always-on).
    The mediating agent (Claude) answers on behalf of the user.

    Design: Search Cognition Theory §2.1 (kernel/search_cognition.md)
    """
    prompt = (
        "You are an epistemic auditor. Analyze this research query for blind spots.\n\n"
        f"Query: {query}\n"
    )
    if context:
        prompt += f"Context: {context}\n"
    prompt += (
        "\nIdentify:\n"
        "1. IMPLICIT ASSUMPTIONS: What does this query take for granted?\n"
        "2. MISSING PERSPECTIVES: What viewpoints or disciplines are absent?\n"
        "3. ALTERNATIVE FRAMINGS: How else could this question be asked?\n\n"
        "Generate 1-3 supplementary search queries that would cover these blind spots.\n"
        "Each query should target a DIFFERENT blind spot.\n\n"
        "Return ONLY the queries, one per line. No numbering, no explanation.\n"
        "If no significant blind spots: NONE"
    )

    text = await _llm_ask(prompt, model="gemini-2.0-flash", max_tokens=256)

    if not text or "NONE" in text.upper().strip():
        logger.info("Φ1: No significant blind spots detected for %r", query)
        return []

    blind_spot_queries = [
        line.strip()
        for line in text.strip().split("\n")
        if line.strip() and len(line.strip()) > 5
    ]
    blind_spot_queries = blind_spot_queries[:3]  # Cap at 3

    if blind_spot_queries:
        logger.info(
            "Φ1: Detected %d blind spots for %r: %s",
            len(blind_spot_queries), query, blind_spot_queries,
        )

    return blind_spot_queries


@dataclass
class DecisionFrame:
    """Φ4: 収束思考 — Structured decision support frame.

    Transforms synthesis (What is known) into judgment support (What to decide).
    The subject (Creator + Claude) makes the final judgment.
    """

    key_findings: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    decision_options: list[str] = field(default_factory=list)
    confidence: float = 0.0
    blind_spots_addressed: int = 0


async def _phi4_convergent_framing(
    query: str,
    synthesis_text: str,
) -> DecisionFrame:
    """Φ4: 収束思考 — Structure synthesis into decision support.

    Transforms "what we found" into "what to decide".
    The subject (Creator + Claude) retains judgment authority.

    Design: Search Cognition Theory §2.1 (kernel/search_cognition.md)
    """
    prompt = (
        "You are a decision support analyst. Given a research synthesis, "
        "structure it for human judgment.\n\n"
        f"Research query: {query}\n\n"
        f"Synthesis:\n{synthesis_text[:50000]}\n\n"
        "Provide EXACTLY this structure (use these exact headers):\n\n"
        "KEY FINDINGS:\n- (3-5 most important findings)\n\n"
        "OPEN QUESTIONS:\n- (2-4 questions that remain unanswered)\n\n"
        "DECISION OPTIONS:\n- (2-3 actionable options the reader could take)\n\n"
        "CONFIDENCE: (0-100, how well does the evidence support a conclusion?)\n"
    )

    text = await _llm_ask(prompt, model="gemini-2.0-flash", max_tokens=512)

    frame = DecisionFrame()
    if not text:
        return frame

    current_section = ""
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        upper = line.upper()
        if "KEY FINDINGS" in upper:
            current_section = "findings"
            continue
        elif "OPEN QUESTIONS" in upper:
            current_section = "questions"
            continue
        elif "DECISION OPTIONS" in upper:
            current_section = "options"
            continue
        elif "CONFIDENCE" in upper:
            import re
            # Match "CONFIDENCE: 80" or "**Confidence**: 80%"
            confidence_match = re.search(r"CONFIDENCE.*?(\d+)", upper)
            if confidence_match:
                frame.confidence = min(int(confidence_match.group(1)), 100) / 100.0
            continue

        # Strip bullet markers
        if line.startswith(("- ", "* ", "• ")):
            line = line[2:].strip()
        elif len(line) > 2 and line[0].isdigit() and line[1] in ".):":
            line = line[2:].strip()

        if current_section == "findings" and line:
            frame.key_findings.append(line)
        elif current_section == "questions" and line:
            frame.open_questions.append(line)
        elif current_section == "options" and line:
            frame.decision_options.append(line)

    logger.info(
        "Φ4: DecisionFrame generated (%d findings, %d questions, %d options, %.0f%% confidence)",
        len(frame.key_findings), len(frame.open_questions),
        len(frame.decision_options), frame.confidence * 100,
    )
    return frame


@dataclass
class ResearchReport:
    """Complete research report from Periskopē."""

    query: str
    search_results: list[SearchResult] = field(default_factory=list)
    synthesis: list[SynthesisResult] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    divergence: DivergenceReport | None = None
    decision_frame: DecisionFrame | None = None
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
                lines.append(f"- ⚠️ Divergence: {'; '.join(self.divergence.divergent_claims)}")
            lines.append("")

        # Decision Frame (Φ4)
        if self.decision_frame:
            df = self.decision_frame
            lines.append("## Φ4 Decision Frame")
            lines.append("")
            if df.key_findings:
                lines.append("### Key Findings")
                for f in df.key_findings:
                    lines.append(f"- {f}")
                lines.append("")
            if df.open_questions:
                lines.append("### Open Questions")
                for q in df.open_questions:
                    lines.append(f"- ❓ {q}")
                lines.append("")
            if df.decision_options:
                lines.append("### Decision Options")
                for o in df.decision_options:
                    lines.append(f"- ➡️ {o}")
                lines.append("")
            lines.append(f"**Confidence**: {df.confidence:.0%}")
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
    - Standard: SearXNG + Brave + Tavily + Gnōsis + Gemini Flash
    - Deep: All searchers + multi-model + citation verification
    """

    def __init__(
        self,
        searxng_url: str = "http://localhost:8888",
        synth_models: list[SynthModel] | None = None,
        max_results_per_source: int = 10,
        verify_citations: bool = True,
    ) -> None:
        # P8: Load config from yaml
        self._config = self._load_config()

        self.max_results = max_results_per_source
        self.verify_citations = verify_citations

        # Searchers
        self.searxng = SearXNGSearcher(base_url=searxng_url)

        self.brave = BraveSearcher()
        self.tavily = TavilySearcher()
        self.semantic_scholar = SemanticScholarSearcher()
        self.gnosis = GnosisSearcher()
        self.sophia = SophiaSearcher()
        self.kairos = KairosSearcher()

        # Synthesizer — depth-level model routing from config
        gemini_model = self._config.get("synthesis", {}).get(
            "gemini_model", "gemini-3-pro-preview",
        )
        self.synthesizer = MultiModelSynthesizer(
            synth_models=synth_models,  # None = use depth routing
            gemini_model=gemini_model,
        )

        # Citation Agent
        self.citation_agent = CitationAgent()

        # Query Expander (W3)
        expansion_model = self._config.get("expansion_model", "gemini-2.0-flash")
        self.query_expander = QueryExpander(model=expansion_model)

        # Page Fetcher (W7: selective deep-read crawling)
        crawl_config = self._config.get("crawling", {})
        self.page_fetcher = PageFetcher(
            timeout=crawl_config.get("timeout", 10.0),
            max_content_length=crawl_config.get("max_content_length", 15_000),
            min_content_length=crawl_config.get("min_content_length", 500),
            playwright_fallback=crawl_config.get("playwright_fallback", True),
        )

        # Embedder cache (P1: avoid re-loading BGE-M3 per rerank call)
        self._embedder = None  # Lazy-initialized

        # Search result cache (P4: avoid duplicate queries in multi-pass)
        self._search_cache: dict[str, tuple[list[SearchResult], dict[str, int]]] = {}

    @staticmethod
    def _load_config() -> dict:
        """P8: Load config.yaml from package directory."""
        from pathlib import Path
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            import yaml
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        return {}


    async def research(
        self,
        query: str,
        sources: list[str] | None = None,
        auto_digest: bool = False,
        digest_depth: str = "quick",
        expand_query: bool = True,
        multipass: bool = False,
        depth: int = 2,
    ) -> ResearchReport:
        """Execute the full research pipeline.

        Args:
            query: Research query.
            sources: List of source names to use. If None, uses all.
                Valid: "searxng", "brave", "tavily", "semantic_scholar",
                    "gnosis", "sophia", "kairos"
            auto_digest: If True, write results to Digestor incoming/ as eat_*.md.
            digest_depth: Digest template depth — "quick" (/eat-), "standard" (/eat), "deep" (/eat+).
            expand_query: If True, expand query via bilingual translation (W3).
            multipass: If True, perform 2-pass search for deeper coverage (W6).
            depth: HGK depth level (1=L1 Quick, 2=L2 Standard, 3=L3 Deep).
                Controls model selection for synthesis.

        Returns:
            ResearchReport with all phases completed.
        """
        start = time.monotonic()
        enabled = set(sources or [
            "searxng", "brave", "tavily", "semantic_scholar",
            "gnosis", "sophia", "kairos",
        ])

        # Fix 4: Depth-based max_results scaling
        # L1=10, L2=20, L3=30 per source
        depth_max = {1: 10, 2: 20, 3: 30}.get(depth, 20)
        effective_max = max(self.max_results, depth_max)
        original_max = self.max_results
        self.max_results = effective_max
        logger.info(
            "Depth L%d: max_results=%d/source (scaled from %d)",
            depth, effective_max, original_max,
        )

        # Phase 0: Φ1 — Blind spot analysis (無知のリマインド)
        # Always-on pipeline step: detects query blind spots and generates
        # supplementary queries. Claude mediates (二重 Copilot 構造).
        blind_spot_queries: list[str] = []
        if depth >= 2:  # L2+ only
            try:
                blind_spot_queries = await _phi1_blind_spot_analysis(query)
                if blind_spot_queries:
                    logger.info(
                        "Phase 0 (Φ1): %d blind-spot queries generated",
                        len(blind_spot_queries),
                    )
            except Exception as e:
                logger.warning("Phase 0 (Φ1) failed: %s", e)

        # Phase 0.5: Query expansion (W3)
        queries = [query]
        if expand_query:
            try:
                queries = await self.query_expander.expand(query)
                if len(queries) > 1:
                    logger.info("Phase 0.5: Query expanded to %d variants", len(queries))
            except Exception as e:
                logger.warning("Query expansion failed, using original: %s", e)

        # Merge Φ1 blind-spot queries into the query set (deduplicated)
        if blind_spot_queries:
            existing = {q.lower() for q in queries}
            for bq in blind_spot_queries:
                if bq.lower() not in existing:
                    queries.append(bq)
                    existing.add(bq.lower())
            logger.info(
                "Phase 0.5+Φ1: Total %d queries (original + expanded + blind-spots)",
                len(queries),
            )

        # Phase 1: Parallel search (across all query variants)
        logger.info("Phase 1: Parallel search for %r (sources: %s)", query, enabled)
        all_results: list[SearchResult] = []
        all_counts: dict[str, int] = {}
        for q in queries:
            results, counts = await self._phase_search(q, enabled)
            all_results.extend(results)
            for k, v in counts.items():
                all_counts[k] = all_counts.get(k, 0) + v
        search_results = all_results
        source_counts = all_counts

        # Phase 1.5: Cross-source deduplication (F11)
        if search_results:
            before = len(search_results)
            search_results = self._deduplicate_results(search_results)
            if len(search_results) < before:
                logger.info("  Dedup: %d → %d results", before, len(search_results))

        # Phase 1.7: Semantic reranking (W4)
        if search_results:
            search_results = self._rerank_results(query, search_results)

        # Phase 1.75: Internal source noise filter (Fix 2)
        # Internal sources (gnosis/sophia/kairos) often return low-relevance
        # documents (handoffs, FM docs, etc). Filter by relevance threshold.
        if search_results:
            min_relevance = 0.3
            before = len(search_results)
            search_results = [
                r for r in search_results
                if r.relevance >= min_relevance
                or (r.source.value if hasattr(r.source, "value") else str(r.source))
                not in INTERNAL_SOURCES
            ]
            filtered = before - len(search_results)
            if filtered:
                logger.info(
                    "Phase 1.75: Filtered %d low-relevance internal results",
                    filtered,
                )

        if not search_results:
            logger.warning("No search results found for %r", query)
            return ResearchReport(
                query=query,
                elapsed_seconds=time.monotonic() - start,
                source_counts=source_counts,
            )

        # Phase 1.6 + 1.8: Summary→Full-text (W7)
        # L2+: Synthesize from snippets, then selectively crawl full pages
        if depth >= 2 and search_results:
            try:
                deep_read_urls = await self._select_urls_for_deep_read(
                    query, search_results, depth=depth,
                )
                if deep_read_urls:
                    logger.info(
                        "Phase 1.8: Deep-reading %d URLs",
                        len(deep_read_urls),
                    )
                    fetched = await self.page_fetcher.fetch_many(deep_read_urls)
                    # Replace snippet with full content
                    enriched = 0
                    for r in search_results:
                        if r.url and r.url in fetched:
                            r.content = fetched[r.url]
                            enriched += 1
                    if enriched:
                        logger.info(
                            "Phase 1.8: Enriched %d results with full content",
                            enriched,
                        )
            except Exception as e:
                logger.warning("Phase 1.6-1.8 (deep-read) failed: %s", e)

        # Phase 2: Multi-model synthesis (depth-level routing)
        from mekhane.periskope.synthesizer import models_for_depth
        if not self.synthesizer.synth_models:
            self.synthesizer.synth_models = models_for_depth(depth)
        logger.info(
            "Phase 2: Multi-model synthesis (%d results, depth=L%d, models=%s)",
            len(search_results), depth,
            [m.value for m in self.synthesizer.synth_models],
        )
        synthesis = await self.synthesizer.synthesize(query, search_results)
        divergence = self.synthesizer.detect_divergence(synthesis)

        # Phase 2.5: Multi-pass refinement (W6)
        # L3: auto-enable multipass; L2: only if explicitly requested
        do_multipass = (multipass or depth >= 3) and synthesis
        max_iterations = 2 if depth >= 3 else 1
        if do_multipass:
            try:
                for iteration in range(max_iterations):
                    refinement_queries = await self._generate_refinement_queries(
                        query, synthesis, search_results,
                    )
                    if not refinement_queries:
                        logger.info("Phase 2.5: No gaps found, stopping iteration")
                        break

                    logger.info(
                        "Phase 2.5 [iter %d/%d]: %d refinement queries",
                        iteration + 1, max_iterations, len(refinement_queries),
                    )
                    for rq in refinement_queries:
                        extra_results, extra_counts = await self._phase_search(
                            rq, enabled,
                        )
                        if extra_results:
                            extra_results = self._deduplicate_results(
                                search_results + extra_results,
                            )
                            existing_urls = {
                                (r.url or "").lower() for r in search_results
                            }
                            new_results = [
                                r for r in extra_results
                                if (r.url or "").lower() not in existing_urls
                            ]
                            search_results.extend(new_results)
                            for k, v in extra_counts.items():
                                source_counts[k] = source_counts.get(k, 0) + v

                    # Deep-read new results too (if L2+)
                    if depth >= 2 and search_results:
                        try:
                            new_urls = await self._select_urls_for_deep_read(
                                query, search_results, depth=depth,
                            )
                            if new_urls:
                                fetched = await self.page_fetcher.fetch_many(new_urls)
                                for r in search_results:
                                    if r.url and r.url in fetched:
                                        r.content = fetched[r.url]
                        except Exception:
                            pass  # Best-effort

                    # Re-synthesize with expanded + enriched results
                    synthesis = await self.synthesizer.synthesize(
                        query, search_results,
                    )
                    divergence = self.synthesizer.detect_divergence(synthesis)
                    logger.info(
                        "Phase 2.5 [iter %d]: %d total results",
                        iteration + 1, len(search_results),
                    )
            except Exception as e:
                logger.warning("Multi-pass refinement failed: %s", e)

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
                    extracted, source_contents, verify_depth=2,
                )
                citations.extend(verified)

        elapsed = time.monotonic() - start
        logger.info("Research complete in %.1fs", elapsed)

        # Phase 3.5: Φ4 — Convergent framing (収束思考)
        # Structure synthesis into decision support for the subject.
        decision_frame = None
        if depth >= 2 and synthesis:
            try:
                synth_text = "\n\n".join(s.content for s in synthesis)
                decision_frame = await _phi4_convergent_framing(query, synth_text)
            except Exception as e:
                logger.warning("Phase 3.5 (Φ4) failed: %s", e)

        report = ResearchReport(
            query=query,
            search_results=search_results,
            synthesis=synthesis,
            citations=citations,
            divergence=divergence,
            decision_frame=decision_frame,
            elapsed_seconds=elapsed,
            source_counts=source_counts,
        )

        # Phase 4: Auto-digest (optional)
        if auto_digest and synthesis:
            logger.info("Phase 4: Auto-digest → incoming/ (depth=%s)", digest_depth)
            digest_path = self._phase_digest(report, depth=digest_depth)
            if digest_path:
                logger.info("  → %s", digest_path)

        return report

    async def _phase_search(
        self,
        query: str,
        enabled: set[str],
    ) -> tuple[list[SearchResult], dict[str, int]]:
        """Phase 1: Execute parallel searches."""
        # P4: Cache key based on query + sources
        cache_key = f"{query}||{'|'.join(sorted(enabled))}"
        if cache_key in self._search_cache:
            cached_results, cached_counts = self._search_cache[cache_key]
            logger.info("P4: Cache hit for %r (%d results)", query, len(cached_results))
            return cached_results, cached_counts

        tasks = {}

        if "searxng" in enabled:
            searxng_weights = self._config.get("searxng", {}).get("weights")
            tasks["searxng"] = self.searxng.search_multi_category(
                query, max_results=self.max_results, weights=searxng_weights,
            )

        if "brave" in enabled and self.brave.available:
            tasks["brave"] = self.brave.search(query, max_results=self.max_results)
        if "tavily" in enabled and self.tavily.available:
            tasks["tavily"] = self.tavily.search(query, max_results=self.max_results)
        if "semantic_scholar" in enabled:
            # S2 API works best with short keyword queries (< 200 chars)
            # Strip explanatory text after colons and truncate
            s2_query = query.split(":")[0].strip() if ":" in query else query
            s2_query = s2_query[:200]
            tasks["semantic_scholar"] = self.semantic_scholar.search(
                s2_query, max_results=self.max_results,
            )
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

        # P4: Cache the results
        self._search_cache[cache_key] = (all_results, source_counts)

        return all_results, source_counts

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize URL for deduplication."""
        url = url.lower().strip()
        # Remove trailing slash
        url = url.rstrip("/")
        # Remove common tracking params
        if "?" in url:
            base, _ = url.split("?", 1)
            return base
        return url

    def _deduplicate_results(
        self, results: list[SearchResult],
    ) -> list[SearchResult]:
        """F11: Cross-source deduplication by URL normalization."""
        seen: set[str] = set()
        deduped: list[SearchResult] = []

        for r in results:
            key = self._normalize_url(r.url) if r.url else f"title:{r.title}"
            if key not in seen:
                seen.add(key)
                deduped.append(r)

        return deduped

    def _rerank_results(
        self,
        query: str,
        results: list[SearchResult],
    ) -> list[SearchResult]:
        """W4: Rerank results using BGE-M3 semantic similarity.

        Replaces position-based relevance with embedding-based similarity
        for cross-source comparable scoring.
        """
        try:
            if self._embedder is None:
                from mekhane.anamnesis.index import Embedder
                self._embedder = Embedder()
                logger.info("W4: BGE-M3 Embedder initialized")

            query_vec = self._embedder.embed(query)

            for r in results:
                text = f"{r.title} {r.snippet or r.content[:200] if r.content else ''}"
                doc_vec = self._embedder.embed(text)
                # Cosine similarity (BGE-M3 vectors are L2-normalized)
                sim = sum(a * b for a, b in zip(query_vec, doc_vec))
                r.relevance = max(0.0, min(1.0, sim))

            results.sort(key=lambda r: r.relevance, reverse=True)
            logger.info("W4: Reranked %d results via BGE-M3", len(results))

        except Exception as e:
            logger.warning("W4: Reranking unavailable, keeping original order: %s", e)

        return results

    async def _generate_refinement_queries(
        self,
        original_query: str,
        synthesis: list[SynthesisResult],
        results: list[SearchResult],
    ) -> list[str]:
        """W6: Generate refinement queries for multi-pass search.

        Analyzes first-pass synthesis to identify gaps and produces
        targeted follow-up queries for deeper coverage.

        Returns:
            List of 1-3 refinement queries, or empty if unnecessary.
        """
        # Build context from synthesis
        synth_summary = "\n".join(
            s.content[:500] for s in synthesis[:2]
        )

        prompt = (
            "You are a research gap analysis assistant.\n"
            f"Original query: {original_query}\n"
            f"Current synthesis:\n{synth_summary}\n\n"
            "Analyze the synthesis for:\n"
            "1. Claims made WITHOUT supporting evidence\n"
            "2. Topics mentioned but not deeply explored\n"
            "3. Counter-arguments or alternative perspectives not addressed\n\n"
            "Generate 2-3 targeted search queries to fill these gaps.\n"
            "If the synthesis already covers the topic thoroughly, return NONE.\n\n"
            "Return ONLY the queries, one per line. No numbering or explanation.\n"
            "If no gaps: NONE"
        )

        try:
            text = await _llm_ask(prompt, max_tokens=256)

            if not text or "NONE" in text.upper().strip():
                return []

            queries = [
                line.strip()
                for line in text.strip().split("\n")
                if line.strip() and len(line.strip()) > 5
            ]
            return queries[:3]  # Cap at 3

        except Exception as e:
            logger.warning("W6: Refinement query generation failed: %s", e)
            return []

    async def _select_urls_for_deep_read(
        self,
        query: str,
        search_results: list[SearchResult],
        depth: int = 2,
    ) -> list[str]:
        """W7: Select URLs that deserve full-text deep reading.

        Summary→Full-text pattern: LLM analyzes snippets
        and decides which pages should be read in full.

        Only external URLs with insufficient content are considered.
        Internal sources (Gnosis/Sophia/Kairos) already have full text.

        Returns:
            List of URLs to crawl (max 5 for L2, max 8 for L3).
        """
        max_deep_read = 5 if depth <= 2 else 8

        # Filter candidates: external sources with short content only
        candidates = []
        for i, r in enumerate(search_results):
            source_name = r.source.value if hasattr(r.source, "value") else str(r.source)
            if source_name in INTERNAL_SOURCES:
                continue  # Already has full content
            if not r.url:
                continue
            if r.content and len(r.content) >= 1000:
                continue  # Already has substantial content
            candidates.append((i, r))

        if not candidates:
            logger.info("W7: No URLs need deep reading (all have sufficient content)")
            return []

        # Build numbered list for LLM
        result_list = []
        for idx, (i, r) in enumerate(candidates[:20]):  # Max 20 candidates
            snippet = (r.snippet or r.content or "")[:150]
            result_list.append(
                f"[{idx + 1}] {r.title}\n"
                f"    URL: {r.url}\n"
                f"    Snippet: {snippet}"
            )

        prompt = (
            "You are a research assistant deciding which web pages to read in full.\n\n"
            f"Research query: {query}\n\n"
            "Search results (summaries only):\n"
            + "\n".join(result_list)
            + "\n\n"
            f"Which pages should be read in full to best answer the query? "
            f"Select up to {max_deep_read} pages.\n\n"
            "Consider:\n"
            "- Pages likely to contain detailed analysis or original data\n"
            "- Pages from authoritative sources (academic, official docs)\n"
            "- Pages whose snippets suggest they cover key aspects of the query\n\n"
            "If the snippets already provide enough information, return NONE.\n\n"
            f"Return ONLY the numbers (comma-separated), e.g.: 1, 3, 5\n"
            "If no pages need deep reading: NONE"
        )

        try:
            text = await _llm_ask(prompt, max_tokens=128)

            if not text or "NONE" in text.upper().strip():
                logger.info("W7: LLM decided no deep reading needed")
                return []

            # Parse selected numbers
            import re
            numbers = re.findall(r"\d+", text)
            selected_indices = [int(n) - 1 for n in numbers if n.isdigit()]

            urls = []
            for idx in selected_indices:
                if 0 <= idx < len(candidates):
                    urls.append(candidates[idx][1].url)
                if len(urls) >= max_deep_read:
                    break

            logger.info(
                "W7: LLM selected %d URLs for deep reading",
                len(urls),
            )
            return urls

        except Exception as e:
            logger.warning("W7: URL selection failed, falling back to top-N: %s", e)
            # Fallback: top N external URLs by relevance
            return [
                r.url for _, r in candidates[:max_deep_read]
                if r.url
            ]

    @staticmethod
    def _classify_query(query: str) -> str:
        """F12: Classify query type for adaptive source selection.

        Returns:
            "academic", "implementation", "news", or "concept".
        """
        q = query.lower()
        academic_kw = ["paper", "arxiv", "研究", "論文", "experiment", "study", "journal"]
        impl_kw = ["実装", "code", "how to", "作り方", "tutorial", "library", "方法"]
        news_kw = ["latest", "最新", "news", "ニュース", "announce", "release", "update"]

        # news > academic > implementation (news keywords override academic)
        if any(kw in q for kw in news_kw):
            return "news"
        if any(kw in q for kw in academic_kw):
            return "academic"
        if any(kw in q for kw in impl_kw):
            return "implementation"
        return "concept"

    @classmethod
    def select_sources(cls, query: str) -> list[str]:
        """F12: Suggest optimal sources based on query classification."""
        qtype = cls._classify_query(query)

        if qtype == "academic":
            return ["gnosis", "semantic_scholar", "searxng", "brave"]
        elif qtype == "implementation":
            return ["searxng", "brave", "sophia"]
        elif qtype == "news":
            return ["searxng", "brave", "tavily"]
        else:
            return ["searxng", "brave", "tavily", "semantic_scholar", "gnosis", "sophia", "kairos"]



    def _phase_digest(self, report: ResearchReport, depth: str = "quick") -> Path | None:
        """Phase 4: Write research results to Digestor incoming.

        Creates an eat_*.md file in ~/oikos/mneme/.hegemonikon/incoming/
        compatible with the /eat workflow (F⊣G adjunction).

        Args:
            report: Completed research report.
            depth: Template depth — "quick" (/eat-), "standard" (/eat), "deep" (/eat+).

        Returns:
            Path to the created file, or None on failure.
        """
        try:
            incoming_dir = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "incoming"
            incoming_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d")
            safe_query = "".join(
                ch if ch.isalnum() or ch in "-_ " else ""
                for ch in report.query[:40]
            ).strip().replace(" ", "_")
            filename = f"eat_{timestamp}_periskope_{safe_query}.md"
            filepath = incoming_dir / filename

            if filepath.exists():
                logger.info("Digest file already exists: %s", filename)
                return filepath

            # Build synthesis content
            synth_content = ""
            confidence = 0.0
            for s in report.synthesis:
                synth_content += s.content + "\n\n"
                confidence = max(confidence, s.confidence)

            # Citation summary
            citation_lines = []
            for c in report.citations:
                score = f"{c.similarity:.0%}" if c.similarity is not None else "—"
                citation_lines.append(
                    f"| {c.claim[:50]}... | {c.taint_level.value} | {score} |"
                )
            citation_table = ""
            if citation_lines:
                citation_table = (
                    "| Claim | Level | Score |\n"
                    "|:------|:------|------:|\n"
                    + "\n".join(citation_lines[:10])
                )

            # Decision Frame (Φ4)
            decision_frame_md = ""
            if report.decision_frame:
                df = report.decision_frame
                decision_frame_md = "## Φ4 Decision Frame\n\n"
                if df.key_findings:
                    decision_frame_md += "### Key Findings\n"
                    decision_frame_md += "\n".join(f"- {f}" for f in df.key_findings)
                    decision_frame_md += "\n\n"
                if df.open_questions:
                    decision_frame_md += "### Open Questions\n"
                    decision_frame_md += "\n".join(f"- ❓ {q}" for q in df.open_questions)
                    decision_frame_md += "\n\n"
                if df.decision_options:
                    decision_frame_md += "### Decision Options\n"
                    decision_frame_md += "\n".join(f"- ➡️ {o}" for o in df.decision_options)
                    decision_frame_md += "\n\n"
                decision_frame_md += f"**Confidence**: {df.confidence:.0%}\n\n"

            # Source count
            sources_str = ", ".join(
                f"{k}: {v}" for k, v in report.source_counts.items()
            )

            # Depth-dependent sections
            if depth == "deep":
                phase_template = self._deep_template()
            elif depth == "standard":
                phase_template = self._standard_template()
            else:
                phase_template = self._quick_template()

            content = f"""---
title: "Periskopē: {report.query[:60]}"
source: periskope
url: N/A
score: {confidence:.2f}
matched_topics: [periskope_research]
digest_to: []
generated: {timestamp}
depth: {depth}
---

# /eat 候補: Periskopē Research — {report.query[:60]}

> **Confidence**: {confidence:.0%} | **Sources**: {sources_str}
> **Elapsed**: {report.elapsed_seconds:.1f}s | **Results**: {len(report.search_results)}
> **Depth**: {depth} | **Auto-generated by Periskopē → /eat auto-digest**

## Synthesis

{synth_content.strip()}

## Citation Verification

{citation_table or '(no citations verified)'}

{decision_frame_md}

{phase_template}

---

*Auto-generated by Periskopē auto-digest ({timestamp}, depth={depth})*
*消化するには: `/eat` で読み込み、上記のテンプレートに従って統合*
"""
            filepath.write_text(content, encoding="utf-8")
            return filepath

        except Exception as e:
            logger.error("Auto-digest failed: %s", e)
            return None

    @staticmethod
    def _quick_template() -> str:
        """Quick /eat- template — minimal Phase 0."""
        return """## Phase 0: 圏の特定

| 項目 | 内容 |
|:-----|:-----|
| 圏 Ext | <!-- 外部構造 --> |
| 圏 Int | <!-- 内部構造 --> |
| F (取込) | <!-- Ext → Int --> |
| G (忘却) | <!-- Int → Ext --> |"""

    @staticmethod
    def _standard_template() -> str:
        """Standard /eat template — Phase 0 + /fit checklist."""
        return """## Phase 0: 圏の特定 (テンプレート)

| 項目 | 内容 |
|:-----|:-----|
| 圏 Ext (外部構造) | <!-- Periskopē が収集した研究知見 --> |
| 圏 Int (内部構造) | <!-- HGK 内の対応する圏 --> |
| 関手 F (取込) | <!-- Ext → Int へのマッピング --> |
| 関手 G (忘却) | <!-- Int → Ext への写像 --> |
| η (情報保存) | <!-- 取り込んで忘却→元情報をどの程度復元できるか --> |
| ε (構造保存) | <!-- 忘却して取込→HGK構造がどの程度維持されるか --> |

## /fit チェックリスト

- [ ] η 検証: 研究知見が HGK 内で再現可能
- [ ] ε 検証: HGK 既存構造との整合性確認
- [ ] Drift 測定: 1-ε の許容範囲内"""

    @staticmethod
    def _deep_template() -> str:
        """Deep /eat+ template — full 7-phase digestion."""
        return """## Phase 0: 圏の特定

| 項目 | 内容 |
|:-----|:-----|
| 圏 Ext (外部構造) | <!-- Periskopē が収集した研究知見 --> |
| 圏 Int (内部構造) | <!-- HGK 内の対応する圏 --> |
| 関手 F (取込) | <!-- Ext → Int へのマッピング --> |
| 関手 G (忘却) | <!-- Int → Ext への写像 --> |
| η (情報保存) | <!-- 取り込んで忘却→元情報をどの程度復元できるか --> |
| ε (構造保存) | <!-- 忘却して取込→HGK構造がどの程度維持されるか --> |

## Phase 1: 構造抽出

> 主要概念・メカニズム・依存関係を構造化抽出する。

- [ ] 主要概念の列挙
- [ ] 依存関係グラフ (概念間)
- [ ] HGK 既存概念との対応付け

## Phase 2: 変換設計 (F: Ext → Int)

> 外部知見を HGK 内部構造にマッピングする具体設計。

- [ ] T1: 既知の再発見 (Rediscovery)
- [ ] T2: 既知の拡張 (Extension)
- [ ] T3: 新規概念 (Novel)
- [ ] T4: 不要/矛盾 (Reject)

## Phase 3: 忘却設計 (G: Int → Ext)

> HGK 構造から外部に投影したとき何が失われるかを分析。

- [ ] 忘却される情報の特定
- [ ] 許容できる情報損失の判定
- [ ] 情報保存の対策

## Phase 4: 統合検証

- [ ] η 検証: F→G→F = id (情報保存)
- [ ] ε 検証: G→F→G = id (構造保存)
- [ ] Drift 測定: 1-ε の許容範囲内
- [ ] 構造整合性確認

## Phase 5: 行動提案

- [ ] 実装すべき変更のリスト
- [ ] 優先順位付け
- [ ] 見積もり

## Phase 6: 反芻

- [ ] 消化プロセスの振り返り
- [ ] 信念更新 (/dox)
- [ ] 知識永続化 (/epi)"""

