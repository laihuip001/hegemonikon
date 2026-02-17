"""
Internal knowledge searcher for Periskopē.

Searches HGK's internal knowledge bases:
- Gnōsis (academic papers via LanceDB)
- Sophia (Knowledge Items via TF-IDF/embedding)
- Kairos (session handoffs and memory)

These searchers access the libraries directly (not via MCP)
for lower latency and richer result data.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from mekhane.periskope.models import SearchResult, SearchSource

logger = logging.getLogger(__name__)

# Ensure project root is in path
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


class GnosisSearcher:
    """Search Gnōsis academic paper index (LanceDB).

    Wraps mekhane.anamnesis.index.GnosisIndex for direct access
    to the paper database without MCP overhead.
    """

    def __init__(self) -> None:
        self._index = None

    def _get_index(self):
        """Lazy-load GnosisIndex."""
        if self._index is None:
            try:
                from mekhane.anamnesis.index import GnosisIndex
                self._index = GnosisIndex()
            except Exception as e:
                logger.error("Failed to initialize GnosisIndex: %s", e)
                raise
        return self._index

    async def search(
        self,
        query: str,
        max_results: int = 10,
        source_filter: str | None = None,
    ) -> list[SearchResult]:
        """Search Gnōsis paper index.

        Args:
            query: Search query.
            max_results: Maximum results to return.
            source_filter: Filter by source (arxiv, semantic_scholar, etc.).

        Returns:
            List of SearchResult from Gnōsis.
        """
        try:
            index = self._get_index()
            raw_results = index.search(query, k=max_results, source_filter=source_filter)
        except Exception as e:
            logger.error("Gnōsis search failed: %s", e)
            return []

        results = []
        for i, r in enumerate(raw_results):
            result = SearchResult(
                source=SearchSource.GNOSIS,
                title=r.get("title", "Untitled"),
                url=r.get("url"),
                content=r.get("abstract", ""),
                snippet=_truncate(r.get("abstract", ""), 200),
                relevance=r.get("_distance", 1.0 - (i / max(len(raw_results), 1))),
                timestamp=r.get("published_date"),
                metadata={
                    "authors": r.get("authors", ""),
                    "citations": r.get("citations"),
                    "paper_source": r.get("source", ""),
                    "doi": r.get("doi"),
                    "arxiv_id": r.get("arxiv_id"),
                },
            )
            results.append(result)

        logger.info("Gnōsis: %d results for %r", len(results), query)
        return results


class SophiaSearcher:
    """Search Sophia Knowledge Items (KI) and Steps.

    Wraps the TF-IDF search from sophia_mcp_server for direct access.
    """

    # Default KI directory
    KI_DIR = Path("/home/makaron8426/.gemini/antigravity/knowledge")
    STEPS_ROOT = Path("/home/makaron8426/.gemini/antigravity/brain")

    def __init__(self, ki_dir: Path | None = None) -> None:
        self.ki_dir = ki_dir or self.KI_DIR

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Search Knowledge Items via TF-IDF.

        Args:
            query: Search query.
            max_results: Maximum results to return.

        Returns:
            List of SearchResult from Sophia.
        """
        try:
            docs = self._collect_searchable_docs()
            ranked = self._tfidf_rank(query, docs, k=max_results)
        except Exception as e:
            logger.error("Sophia search failed: %s", e)
            return []

        results = []
        for i, (name, content, path, doc_type, score) in enumerate(ranked):
            result = SearchResult(
                source=SearchSource.SOPHIA,
                title=name,
                url=f"file://{path}" if path else None,
                content=content[:1000],
                snippet=_truncate(content, 200),
                relevance=score,
                metadata={
                    "artifact_type": doc_type,
                    "file_path": str(path) if path else "",
                },
            )
            results.append(result)

        logger.info("Sophia: %d results for %r", len(results), query)
        return results

    def _collect_searchable_docs(self) -> list[tuple[str, str, Path | None, str]]:
        """Collect KI files for search."""
        docs: list[tuple[str, str, Path | None, str]] = []

        if self.ki_dir.exists():
            for f in self.ki_dir.glob("*.md"):
                try:
                    content = f.read_text(encoding="utf-8")
                    docs.append((f.stem, content, f, "knowledge_item"))
                except Exception:
                    continue

        return docs

    def _tfidf_rank(
        self,
        query: str,
        docs: list[tuple[str, str, Path | None, str]],
        k: int = 10,
    ) -> list[tuple[str, str, Path | None, str, float]]:
        """Simple TF-IDF ranking."""
        import re
        from collections import Counter

        query_terms = set(re.findall(r'\w+', query.lower()))
        if not query_terms:
            return []

        scored = []
        for name, content, path, doc_type in docs:
            content_lower = content.lower()
            words = re.findall(r'\w+', content_lower)
            word_counts = Counter(words)
            total = len(words) or 1

            # Simple TF score (normalized frequency of query terms)
            score = sum(word_counts.get(t, 0) / total for t in query_terms)

            # Boost title matches
            name_lower = name.lower()
            title_bonus = sum(1.0 for t in query_terms if t in name_lower) * 0.5
            score += title_bonus

            if score > 0:
                scored.append((name, content, path, doc_type, score))

        scored.sort(key=lambda x: x[4], reverse=True)
        return scored[:k]


class KairosSearcher:
    """Search Kairos session handoffs and ROM files.

    Provides access to session history and accumulated knowledge.
    """

    HANDOFF_DIR = Path("/home/makaron8426/oikos/mneme/.hegemonikon/sessions")
    ROM_DIR = Path("/home/makaron8426/oikos/mneme/.hegemonikon/rom")

    def __init__(
        self,
        handoff_dir: Path | None = None,
        rom_dir: Path | None = None,
    ) -> None:
        self.handoff_dir = handoff_dir or self.HANDOFF_DIR
        self.rom_dir = rom_dir or self.ROM_DIR

    async def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[SearchResult]:
        """Search handoffs and ROM files.

        Args:
            query: Search query.
            max_results: Maximum results.

        Returns:
            List of SearchResult from Kairos.
        """
        docs = self._collect_docs()
        ranked = self._simple_rank(query, docs, k=max_results)

        results = []
        for name, content, path, doc_type, score in ranked:
            result = SearchResult(
                source=SearchSource.KAIROS,
                title=name,
                url=f"file://{path}" if path else None,
                content=content[:1000],
                snippet=_truncate(content, 200),
                relevance=score,
                metadata={
                    "artifact_type": doc_type,
                    "file_path": str(path) if path else "",
                },
            )
            results.append(result)

        logger.info("Kairos: %d results for %r", len(results), query)
        return results

    def _collect_docs(self) -> list[tuple[str, str, Path | None, str]]:
        docs = []

        # Handoffs
        if self.handoff_dir.exists():
            for f in sorted(self.handoff_dir.glob("handoff_*.md"), reverse=True)[:20]:
                try:
                    content = f.read_text(encoding="utf-8")
                    docs.append((f.stem, content, f, "handoff"))
                except Exception:
                    continue

        # ROMs
        if self.rom_dir.exists():
            for f in sorted(self.rom_dir.glob("rom_*.md"), reverse=True)[:20]:
                try:
                    content = f.read_text(encoding="utf-8")
                    docs.append((f.stem, content, f, "rom"))
                except Exception:
                    continue

        return docs

    def _simple_rank(
        self,
        query: str,
        docs: list[tuple[str, str, Path | None, str]],
        k: int = 10,
    ) -> list[tuple[str, str, Path | None, str, float]]:
        """Simple keyword-based ranking."""
        import re
        from collections import Counter

        query_terms = set(re.findall(r'\w+', query.lower()))
        if not query_terms:
            return []

        scored = []
        for name, content, path, doc_type in docs:
            words = re.findall(r'\w+', content.lower())
            counts = Counter(words)
            total = len(words) or 1

            score = sum(counts.get(t, 0) / total for t in query_terms)
            # Boost title matches
            score += sum(0.5 for t in query_terms if t in name.lower())

            if score > 0:
                scored.append((name, content, path, doc_type, score))

        scored.sort(key=lambda x: x[4], reverse=True)
        return scored[:k]


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."
