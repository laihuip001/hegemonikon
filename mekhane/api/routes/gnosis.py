# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: /api/gnosis/* — Gnōsis ベクトル検索エンドポイント
"""
Gnōsis Routes — anamnesis GnosisIndex のラッパー

GET /api/gnosis/search?q=...&limit=10  — ベクトル検索
GET /api/gnosis/stats                   — インデックス統計
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("hegemonikon.api.gnosis")

# PURPOSE: レスポンスモデル
class GnosisSearchResult(BaseModel):
    """検索結果1件。"""
    title: str = ""
    source: str = ""
    authors: str = ""
    abstract: str = ""
    url: str = ""
    citations: str = ""
    score: float | None = None


# PURPOSE: 検索レスポンスモデル
class GnosisSearchResponse(BaseModel):
    """検索レスポンス。"""
    query: str
    results: list[GnosisSearchResult]
    total: int


# PURPOSE: 統計レスポンスモデル
class GnosisStatsResponse(BaseModel):
    """インデックス統計。"""
    total: int = 0
    unique_dois: int = 0
    unique_arxiv: int = 0
    sources: dict[str, int] = {}
    last_collected: str = ""
    available: bool = True
    message: str = ""


router = APIRouter(prefix="/gnosis", tags=["gnosis"])


# PURPOSE: GnosisIndex の遅延初期化 (/dia+ fix #2)
_index = None
_index_error: str | None = None


def _get_index():
    """GnosisIndex を遅延初期化。失敗時は例外メッセージを保持。"""
    global _index, _index_error

    if _index_error is not None:
        raise RuntimeError(_index_error)

    if _index is None:
        try:
            from mekhane.anamnesis.index import GnosisIndex
            _index = GnosisIndex()
            logger.info("GnosisIndex initialized successfully")
        except Exception as exc:
            _index_error = str(exc)
            logger.error("GnosisIndex initialization failed: %s", exc)
            raise

    return _index


# PURPOSE: Gnōsis ベクトル検索
@router.get("/search", response_model=GnosisSearchResponse)
async def gnosis_search(
    q: str = Query(..., min_length=1, description="検索クエリ"),
    limit: int = Query(10, ge=1, le=50, description="結果件数"),
) -> GnosisSearchResponse:
    """Gnōsis ベクトル検索。"""
    try:
        index = _get_index()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Gnōsis index unavailable: {exc}",
        )

    results = index.search(q, k=limit)

    items = [
        GnosisSearchResult(
            title=r.get("title", ""),
            source=r.get("source", ""),
            authors=r.get("authors", ""),
            abstract=r.get("abstract", ""),
            url=r.get("url", ""),
            citations=str(r.get("citations", "")),
            score=r.get("score"),
        )
        for r in results
    ]

    return GnosisSearchResponse(
        query=q,
        results=items,
        total=len(items),
    )


# PURPOSE: Gnōsis インデックス統計
@router.get("/stats", response_model=GnosisStatsResponse)
async def gnosis_stats() -> GnosisStatsResponse:
    """Gnōsis インデックス統計。"""
    try:
        index = _get_index()
    except RuntimeError as exc:
        return GnosisStatsResponse(
            available=False,
            message=f"Index unavailable: {exc}",
        )

    stats = index.stats()

    return GnosisStatsResponse(
        total=stats.get("total", 0),
        unique_dois=stats.get("unique_dois", 0),
        unique_arxiv=stats.get("unique_arxiv", 0),
        sources=stats.get("sources", {}),
        last_collected=stats.get("last_collected_at", ""),
    )
