# PROOF: [L2/探索] <- O3→未知領域の探索→Periskope統合検索
"""
Periskopē data models.

Shared data structures for the search → synthesis → citation pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SearchSource(str, Enum):
    """Search source identifiers."""
    SEARXNG = "searxng"
    BRAVE = "brave"
    TAVILY = "tavily"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    GNOSIS = "gnosis"
    SOPHIA = "sophia"
    KAIROS = "kairos"
    PLAYWRIGHT = "playwright"


class TaintLevel(str, Enum):
    """BC-6 TAINT classification for citations."""
    SOURCE = "SOURCE"       # Directly verified (similarity > 0.8)
    TAINT = "TAINT"         # Partially verified (0.5 < similarity < 0.8)
    FABRICATED = "FABRICATED"  # Not found at source (similarity < 0.5)
    UNCHECKED = "UNCHECKED"   # Not yet verified


class SynthModel(str, Enum):
    """Available synthesis models."""
    GEMINI_FLASH = "gemini-3-flash-preview"
    GEMINI_PRO = "gemini-3-pro-preview"
    CLAUDE_SONNET = "claude-sonnet-4-5"    # L2 standard
    CLAUDE_OPUS = "claude-opus-4-6"        # L3 deep
    # Deprecated — use CLAUDE_SONNET/CLAUDE_OPUS instead
    CLAUDE_LS = "claude-ls"
    CLAUDE_CORTEX = "claude-cortex"


@dataclass
class SearchResult:
    """A single search result from any source."""
    source: SearchSource
    title: str
    url: str | None = None
    content: str = ""
    snippet: str = ""       # Short extract for display
    relevance: float = 0.0  # 0.0-1.0
    timestamp: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_internal(self) -> bool:
        """Whether this result comes from HGK internal knowledge."""
        return self.source in (SearchSource.GNOSIS, SearchSource.SOPHIA, SearchSource.KAIROS)


@dataclass
class Citation:
    """A citation linking a claim to its source."""
    claim: str
    source_url: str
    source_title: str = ""
    taint_level: TaintLevel = TaintLevel.UNCHECKED
    similarity: float | None = None
    verified_at: str | None = None
    verification_note: str = ""

    @property
    def is_trustworthy(self) -> bool:
        return self.taint_level == TaintLevel.SOURCE


@dataclass
class SynthesisResult:
    """Result from a single model's synthesis."""
    model: SynthModel
    content: str
    citations: list[Citation] = field(default_factory=list)
    confidence: float = 0.0
    thinking: str = ""  # Chain-of-thought if available
    token_count: int = 0


@dataclass
class DivergenceReport:
    """Report on divergence between multiple model outputs."""
    models_compared: list[SynthModel] = field(default_factory=list)
    agreement_score: float = 0.0  # 0.0-1.0
    divergent_claims: list[str] = field(default_factory=list)
    consensus_claims: list[str] = field(default_factory=list)


@dataclass
class PeriskopeConfig:
    """Configuration for a Periskopē research session."""
    query: str = ""
    # Search config
    search_sources: list[SearchSource] = field(
        default_factory=lambda: [
            SearchSource.SEARXNG,
            SearchSource.BRAVE,
            SearchSource.TAVILY,
            SearchSource.SEMANTIC_SCHOLAR,
            SearchSource.GNOSIS,
            SearchSource.SOPHIA,
        ]
    )
    max_results_per_source: int = 20
    # Synthesis config
    synth_models: list[SynthModel] = field(
        default_factory=lambda: [SynthModel.GEMINI_FLASH]
    )
    # Citation config
    verify_citations: bool = True
    max_citations_to_verify: int = 10
    # Output config
    output_format: str = "markdown"
    auto_digest: bool = False  # Auto-run /eat- after completion


@dataclass
class PeriskopeReport:
    """Final output of a Periskopē research session."""
    query: str
    config: PeriskopeConfig
    search_results: list[SearchResult] = field(default_factory=list)
    synthesis_results: list[SynthesisResult] = field(default_factory=list)
    divergence: DivergenceReport | None = None
    citations: list[Citation] = field(default_factory=list)
    # Metrics
    total_sources: int = 0
    verified_citations: int = 0
    taint_ratio: float = 0.0  # Fraction of TAINT/FABRICATED citations
    execution_time_seconds: float = 0.0
    report_markdown: str = ""

    @property
    def citation_health(self) -> str:
        """Overall citation health assessment."""
        if self.taint_ratio < 0.1:
            return "🟢 Healthy"
        elif self.taint_ratio < 0.3:
            return "🟡 Moderate"
        else:
            return "🔴 Unreliable"
