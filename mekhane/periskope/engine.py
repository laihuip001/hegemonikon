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
from mekhane.periskope.searchers.exa_searcher import ExaSearcher
from mekhane.periskope.searchers.internal_searcher import (
    GnosisSearcher,
    SophiaSearcher,
    KairosSearcher,
)
from mekhane.periskope.synthesizer import MultiModelSynthesizer
from mekhane.periskope.citation_agent import CitationAgent
from mekhane.periskope.query_expander import QueryExpander

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
        # P8: Load config from yaml
        self._config = self._load_config()

        self.max_results = max_results_per_source
        self.verify_citations = verify_citations

        # Searchers
        self.searxng = SearXNGSearcher(base_url=searxng_url)
        self.exa = ExaSearcher()
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
                Valid: "searxng", "exa", "gnosis", "sophia", "kairos"
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
        enabled = set(sources or ["searxng", "exa", "gnosis", "sophia", "kairos"])

        # Phase 0.5: Query expansion (W3)
        queries = [query]
        if expand_query:
            try:
                queries = await self.query_expander.expand(query)
                if len(queries) > 1:
                    logger.info("Phase 0.5: Query expanded to %d variants", len(queries))
            except Exception as e:
                logger.warning("Query expansion failed, using original: %s", e)

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

        if not search_results:
            logger.warning("No search results found for %r", query)
            return ResearchReport(
                query=query,
                elapsed_seconds=time.monotonic() - start,
                source_counts=source_counts,
            )

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
        if multipass and synthesis:
            try:
                refinement_queries = await self._generate_refinement_queries(
                    query, synthesis, search_results,
                )
                if refinement_queries:
                    logger.info(
                        "Phase 2.5: Multi-pass with %d refinement queries",
                        len(refinement_queries),
                    )
                    for rq in refinement_queries:
                        extra_results, extra_counts = await self._phase_search(
                            rq, enabled,
                        )
                        if extra_results:
                            extra_results = self._deduplicate_results(
                                search_results + extra_results,
                            )
                            # Only keep truly new results
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
                    # Re-synthesize with expanded results
                    synthesis = await self.synthesizer.synthesize(
                        query, search_results,
                    )
                    divergence = self.synthesizer.detect_divergence(synthesis)
                    logger.info(
                        "Phase 2.5 complete: %d total results",
                        len(search_results),
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

        report = ResearchReport(
            query=query,
            search_results=search_results,
            synthesis=synthesis,
            citations=citations,
            divergence=divergence,
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
        if "exa" in enabled:
            exa_weights = self._config.get("exa", {}).get("weights")
            tasks["exa"] = self.exa.search_multi_category(
                query, max_results=self.max_results, weights=exa_weights,
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
            "You are a research query refinement assistant.\n"
            f"Original query: {original_query}\n"
            f"Synthesis summary:\n{synth_summary}\n\n"
            "Based on the synthesis, identify 1-3 specific sub-topics or "
            "gaps that were NOT well covered. Generate targeted search queries "
            "to fill these gaps.\n\n"
            "Return ONLY the queries, one per line. No numbering or explanation."
        )

        try:
            import httpx

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    "http://localhost:8765/api/chat",
                    json={
                        "model": "gemini-2.0-flash",
                        "message": prompt,
                        "max_tokens": 256,
                    },
                )
                response.raise_for_status()
                data = response.json()
                text = data.get("response") or data.get("text") or ""

                queries = [
                    line.strip()
                    for line in text.strip().split("\n")
                    if line.strip() and len(line.strip()) > 5
                ]
                return queries[:3]  # Cap at 3

        except Exception as e:
            logger.warning("W6: Refinement query generation failed: %s", e)
            return []

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
            return ["gnosis", "exa", "searxng"]
        elif qtype == "implementation":
            return ["searxng", "exa", "sophia"]
        elif qtype == "news":
            return ["searxng", "exa"]
        else:
            return ["searxng", "exa", "gnosis", "sophia", "kairos"]

    @classmethod
    def exa_weights_for_query(cls, query: str) -> dict[str, float]:
        """F12: Suggest Exa category weights based on query classification.

        Returns weights dict suitable for ExaSearcher.search_multi_category().
        """
        qtype = cls._classify_query(query)

        if qtype == "academic":
            return {
                "general": 0.15, "paper": 0.50, "github": 0.05,
                "news": 0.05, "tweet": 0.05, "pdf": 0.15, "personal_site": 0.05,
            }
        elif qtype == "implementation":
            return {
                "general": 0.20, "paper": 0.10, "github": 0.40,
                "news": 0.05, "tweet": 0.05, "pdf": 0.10, "personal_site": 0.10,
            }
        elif qtype == "news":
            return {
                "general": 0.20, "paper": 0.05, "github": 0.05,
                "news": 0.40, "tweet": 0.20, "pdf": 0.05, "personal_site": 0.05,
            }
        else:  # concept
            return {
                "general": 0.30, "paper": 0.25, "github": 0.15,
                "news": 0.15, "tweet": 0.05, "pdf": 0.05, "personal_site": 0.05,
            }

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

