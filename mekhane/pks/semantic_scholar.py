#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/pks/ A0→Gnōsis 知識基盤の拡充に学術 API が必要
# PURPOSE: Semantic Scholar API クライアント（論文メタデータの構造化取得）
"""
Semantic Scholar API Client
============================

無料の学術論文検索 API。title, abstract, year, citationCount, DOI を
構造化 JSON で返す。Gnōsis へのバッチ投入に最適。

Usage:
    client = SemanticScholarClient()
    papers = client.search("free energy principle", limit=20)
    papers = client.search("active inference", year_range=(2023, 2026))

API Docs: https://api.semanticscholar.org/api-docs/graph
Rate Limit (unauthenticated): ~100 req/5min (shared pool)
Rate Limit (authenticated): 1 req/sec
"""

from __future__ import annotations

import os
import time
import json
import httpx
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

# PURPOSE: Paper の機能を提供する
@dataclass
class Paper:
    """Semantic Scholar の論文メタデータ"""
    paper_id: str
    title: str
    year: Optional[int] = None
    abstract: Optional[str] = None
    citation_count: int = 0
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    authors: list[str] = field(default_factory=list)

    # PURPOSE: semantic_scholar の to dict 処理を実行する
    def to_dict(self) -> dict:
        return asdict(self)

    # PURPOSE: semantic_scholar の from api 処理を実行する
    @classmethod
    def from_api(cls, data: dict) -> "Paper":
        """API レスポンスから Paper を構築"""
        ext_ids = data.get("externalIds") or {}
        authors_raw = data.get("authors") or []
        return cls(
            paper_id=data.get("paperId", ""),
            title=data.get("title", ""),
            year=data.get("year"),
            abstract=data.get("abstract"),
            citation_count=data.get("citationCount", 0),
            doi=ext_ids.get("DOI"),
            arxiv_id=ext_ids.get("ArXiv"),
            url=data.get("url"),
            authors=[a.get("name", "") for a in authors_raw],
        )

    # PURPOSE: semantic_scholar の has abstract 処理を実行する
    @property
    def has_abstract(self) -> bool:
        return bool(self.abstract and len(self.abstract) > 20)

    def __repr__(self) -> str:
        return f"Paper({self.year} | {self.citation_count}c | {self.title[:60]}...)"


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

API_BASE = "https://api.semanticscholar.org/graph/v1"
DEFAULT_FIELDS = "title,abstract,year,citationCount,externalIds,url,authors"

# Rate limiting
UNAUTHENTICATED_DELAY = 1.0  # seconds between requests
AUTHENTICATED_DELAY = 1.1    # 1 req/sec + margin


# PURPOSE: SemanticScholarClient の機能を提供する
class SemanticScholarClient:
    """Semantic Scholar Academic Graph API クライアント

    Usage:
        client = SemanticScholarClient()
        papers = client.search("free energy principle", limit=50)
        papers = client.bulk_search("active inference", year_range=(2023, 2026))
    """

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
        self._delay = AUTHENTICATED_DELAY if self._api_key else UNAUTHENTICATED_DELAY
        self._last_request_time = 0.0
        self._total_requests = 0

    # PURPOSE: semantic_scholar の authenticated 処理を実行する
    @property
    def authenticated(self) -> bool:
        return bool(self._api_key)

    def _headers(self) -> dict:
        headers = {"Accept": "application/json"}
        if self._api_key:
            headers["x-api-key"] = self._api_key
        return headers

    def _rate_limit(self):
        """リクエスト間の待機"""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._delay:
            time.sleep(self._delay - elapsed)
        self._last_request_time = time.time()
        self._total_requests += 1

    def _get(self, url: str, params: dict) -> dict:
        """GET リクエスト + レート制限 + リトライ"""
        self._rate_limit()
        timeout = httpx.Timeout(30.0, connect=10.0)

        for attempt in range(3):
            try:
                with httpx.Client(timeout=timeout) as client:
                    resp = client.get(url, params=params, headers=self._headers())

                if resp.status_code == 429:
                    # Rate limited — exponential backoff
                    wait = 2 ** (attempt + 1)
                    print(f"  [S2] Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                    continue

                resp.raise_for_status()
                return resp.json()

            except (httpx.HTTPError, httpx.TimeoutException) as e:
                if attempt < 2:
                    wait = 2 ** (attempt + 1)
                    print(f"  [S2] Error: {e}. Retry in {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"  [S2] Failed after 3 attempts: {e}")
                    return {}

        return {}

    # PURPOSE: semantic_scholar の search 処理を実行する
    def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        year_range: Optional[tuple[int, int]] = None,
        fields: str = DEFAULT_FIELDS,
    ) -> list[Paper]:
        """通常検索 (最大100件/リクエスト, offset でページング)

        Args:
            query: 検索クエリ
            limit: 取得件数 (max 100)
            offset: オフセット (max 9999)
            year_range: (start_year, end_year) でフィルタ
            fields: 取得フィールド
        """
        params = {
            "query": query,
            "limit": min(limit, 100),
            "offset": offset,
            "fields": fields,
        }
        if year_range:
            params["year"] = f"{year_range[0]}-{year_range[1]}"

        data = self._get(f"{API_BASE}/paper/search", params)
        papers_raw = data.get("data", [])
        return [Paper.from_api(p) for p in papers_raw]

    # PURPOSE: semantic_scholar の bulk search 処理を実行する
    def bulk_search(
        self,
        query: str,
        year_range: Optional[tuple[int, int]] = None,
        max_papers: int = 100,
        fields: str = DEFAULT_FIELDS,
    ) -> list[Paper]:
        """バルク検索 (ページングトークンで全件取得可能)

        bulk_search は offset の代わりに token で循環する。
        max_papers で上限を設定。
        """
        all_papers: list[Paper] = []
        token = None

        while len(all_papers) < max_papers:
            params: dict = {
                "query": query,
                "limit": min(100, max_papers - len(all_papers)),
                "fields": fields,
            }
            if year_range:
                params["year"] = f"{year_range[0]}-{year_range[1]}"
            if token:
                params["token"] = token

            data = self._get(f"{API_BASE}/paper/search/bulk", params)
            papers_raw = data.get("data", [])

            if not papers_raw:
                break

            all_papers.extend(Paper.from_api(p) for p in papers_raw)
            token = data.get("token")

            if not token:
                break

            print(f"  [S2] Collected {len(all_papers)} papers so far...")

        return all_papers[:max_papers]

    # PURPOSE: paper を取得する
    def get_paper(self, paper_id: str, fields: str = DEFAULT_FIELDS) -> Optional[Paper]:
        """個別論文の詳細取得"""
        data = self._get(f"{API_BASE}/paper/{paper_id}", {"fields": fields})
        if data and "paperId" in data:
            return Paper.from_api(data)
        return None

    # PURPOSE: citations を取得する
    def get_citations(
        self, paper_id: str, limit: int = 50, fields: str = "title,year,citationCount"
    ) -> list[Paper]:
        """被引用論文を取得"""
        params = {"fields": f"citingPaper.{fields}", "limit": min(limit, 1000)}
        data = self._get(f"{API_BASE}/paper/{paper_id}/citations", params)
        citations_raw = data.get("data", [])
        return [
            Paper.from_api(c["citingPaper"])
            for c in citations_raw
            if c.get("citingPaper")
        ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

# PURPOSE: semantic_scholar の main 処理を実行する
def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: semantic_scholar.py search 'query' [--limit N] [--year START-END]")
        return

    cmd = sys.argv[1]
    query = sys.argv[2]

    limit = 20
    year_range = None

    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        limit = int(sys.argv[idx + 1])

    if "--year" in sys.argv:
        idx = sys.argv.index("--year")
        parts = sys.argv[idx + 1].split("-")
        year_range = (int(parts[0]), int(parts[1]))

    client = SemanticScholarClient()

    if cmd == "search":
        papers = client.search(query, limit=limit, year_range=year_range)
        for p in papers:
            abstract_flag = "✅" if p.has_abstract else "❌"
            print(f"  {abstract_flag} [{p.year}] {p.citation_count:>5}c | {p.title[:70]}")
        print(f"\nTotal: {len(papers)} papers")

    elif cmd == "bulk":
        papers = client.bulk_search(query, year_range=year_range, max_papers=limit)
        for p in papers:
            abstract_flag = "✅" if p.has_abstract else "❌"
            print(f"  {abstract_flag} [{p.year}] {p.citation_count:>5}c | {p.title[:70]}")
        print(f"\nTotal: {len(papers)} papers")


if __name__ == "__main__":
    main()
