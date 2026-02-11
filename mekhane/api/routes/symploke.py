#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Symploke 知識統合層の REST API — 統合検索, 人格, Boot コンテキスト
"""
Symploke Routes — 知識統合層 REST API

GET    /api/symploke/search          — Handoff/Sophia/Kairos 統合検索
GET    /api/symploke/persona         — 現在の Persona 状態
GET    /api/symploke/boot-context    — Boot コンテキスト (全軸データ)
GET    /api/symploke/stats           — 知識統合層の統計情報

Note:
    Symploke は mekhane/symploke/ の統合層。
    synergeia/ (マルチエージェント分散実行) とは全く別のモジュール。
"""

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("hegemonikon.api.symploke")
router = APIRouter(prefix="/symploke", tags=["symploke"])

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


# --- Pydantic Models ---


# PURPOSE: 検索結果アイテム
class SearchResultItem(BaseModel):
    """統合検索結果の1件。"""
    id: str
    source: str = Field(description="handoff | sophia | kairos")
    score: float = Field(description="類似度スコア")
    title: str = ""
    snippet: str = Field(default="", description="内容の抜粋")
    metadata: dict = Field(default_factory=dict)


# PURPOSE: 統合検索レスポンス
class SearchResponse(BaseModel):
    """統合検索レスポンス。"""
    query: str
    results: list[SearchResultItem]
    total: int
    sources_searched: list[str]


# PURPOSE: Persona レスポンス
class PersonaResponse(BaseModel):
    """Persona 状態レスポンス。"""
    persona: dict = Field(description="Claude の Persona 状態")
    creator: dict = Field(default_factory=dict, description="Creator プロファイル")


# PURPOSE: Boot コンテキストレスポンス
class BootContextResponse(BaseModel):
    """Boot コンテキストレスポンス。"""
    mode: str
    axes: dict = Field(description="各軸のデータ")
    summary: str = ""


# PURPOSE: 統計レスポンス
class StatsResponse(BaseModel):
    """知識統合層の統計情報。"""
    handoff_count: int = 0
    sophia_index_exists: bool = False
    kairos_index_exists: bool = False
    persona_exists: bool = False
    boot_axes_available: list[str] = Field(default_factory=list)


# --- Routes ---


# PURPOSE: symploke の search 処理を実行する
@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="検索クエリ"),
    k: int = Query(5, ge=1, le=50, description="結果数"),
    sources: str = Query(
        "handoff,sophia,kairos,gnosis,chronos",
        description="検索対象 (カンマ区切り: handoff, sophia, kairos, gnosis, chronos)"
    ),
):
    """Handoff/Sophia/Kairos の統合セマンティック検索。"""
    source_list = [s.strip() for s in sources.split(",")]
    results: list[SearchResultItem] = []
    sources_searched = []

    # Mnēmē SearchEngine 横断検索 (gnosis / chronos)
    mneme_sources = [s for s in source_list if s in ("gnosis", "chronos")]
    if mneme_sources:
        try:
            from mekhane.symploke.search.engine import SearchEngine
            from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
            from mekhane.symploke.indices import (
                GnosisIndex, ChronosIndex, Document,
            )

            engine = SearchEngine()
            for IndexClass, name in [
                (GnosisIndex, "gnosis"),
                (ChronosIndex, "chronos"),
            ]:
                if name in mneme_sources:
                    adapter = EmbeddingAdapter()
                    index = IndexClass(adapter, name, dimension=384)
                    index.initialize()
                    engine.register(index)

            mneme_results = engine.search(q, sources=mneme_sources, k=k)
            for r in mneme_results:
                results.append(SearchResultItem(
                    id=r.doc_id,
                    source=r.source.value,
                    score=r.score,
                    title=r.doc_id,
                    snippet=r.content[:200] if r.content else "",
                    metadata={"mneme": True},
                ))
            sources_searched.extend(mneme_sources)
        except Exception as exc:
            logger.warning("Mnēmē search failed: %s", exc)

    # Handoff 検索
    if "handoff" in source_list:
        try:
            from mekhane.symploke.handoff_search import search_handoffs
            matches = search_handoffs(q, top_k=k)
            for doc, score in matches:
                results.append(SearchResultItem(
                    id=doc.id,
                    source="handoff",
                    score=score,
                    title=doc.metadata.get("primary_task", ""),
                    snippet=doc.content[:200],
                    metadata={
                        "timestamp": doc.metadata.get("timestamp", ""),
                        "file_path": doc.metadata.get("file_path", ""),
                    },
                ))
            sources_searched.append("handoff")
        except Exception as exc:
            logger.warning("Handoff search failed: %s", exc)

    # Sophia 検索
    if "sophia" in source_list:
        try:
            from mekhane.symploke.sophia_ingest import (
                load_sophia_index,
                search_loaded_index,
                DEFAULT_INDEX_PATH as SOPHIA_INDEX,
            )
            if SOPHIA_INDEX.exists():
                adapter = load_sophia_index(str(SOPHIA_INDEX))
                matches = search_loaded_index(adapter, q, top_k=k)
                for r in matches:
                    results.append(SearchResultItem(
                        id=r.metadata.get("doc_id", ""),
                        source="sophia",
                        score=r.score,
                        title=r.metadata.get("ki_name", ""),
                        snippet=r.metadata.get("summary", "")[:200],
                        metadata={
                            "artifact": r.metadata.get("artifact", ""),
                            "file_path": r.metadata.get("file_path", ""),
                        },
                    ))
                sources_searched.append("sophia")
        except Exception as exc:
            logger.warning("Sophia search failed: %s", exc)

    # Kairos 検索
    if "kairos" in source_list:
        try:
            from mekhane.symploke.kairos_ingest import (
                load_kairos_index,
                search_loaded_index as kairos_search,
                DEFAULT_INDEX_PATH as KAIROS_INDEX,
            )
            if KAIROS_INDEX.exists():
                adapter = load_kairos_index(str(KAIROS_INDEX))
                matches = kairos_search(adapter, q, top_k=k)
                for r in matches:
                    results.append(SearchResultItem(
                        id=r.metadata.get("doc_id", ""),
                        source="kairos",
                        score=r.score,
                        title=r.metadata.get("title", r.metadata.get("primary_task", "")),
                        snippet="",
                        metadata={
                            "type": r.metadata.get("type", ""),
                            "timestamp": r.metadata.get("timestamp", ""),
                            "file_path": r.metadata.get("file_path", ""),
                        },
                    ))
                sources_searched.append("kairos")
        except Exception as exc:
            logger.warning("Kairos search failed: %s", exc)

    # スコアでソート
    results.sort(key=lambda x: x.score, reverse=True)
    results = results[:k]

    return SearchResponse(
        query=q,
        results=results,
        total=len(results),
        sources_searched=sources_searched,
    )


# PURPOSE: persona を取得する
@router.get("/persona", response_model=PersonaResponse)
async def get_persona():
    """現在の Persona 状態と Creator プロファイルを取得。"""
    persona_data = {}
    creator_data = {}

    try:
        from mekhane.symploke.persona import load_persona, load_creator_profile
        persona_data = load_persona()
        creator_data = load_creator_profile()
    except Exception as exc:
        logger.warning("Persona load failed: %s", exc)

    return PersonaResponse(persona=persona_data, creator=creator_data)


# PURPOSE: boot context を取得する
@router.get("/boot-context", response_model=BootContextResponse)
async def get_boot_context(
    mode: str = Query("standard", description="fast | standard | detailed"),
    context: Optional[str] = Query(None, description="セッションコンテキスト"),
):
    """Boot コンテキスト (全軸データ) を取得。"""
    try:
        from mekhane.symploke.boot_integration import get_boot_context as _get_ctx
        result = _get_ctx(mode=mode, context=context)

        # numpy.float32 等の非JSON型を sanitize
        sanitized = json.loads(json.dumps(result, default=str))

        return BootContextResponse(
            mode=mode,
            axes=sanitized,
            summary=f"Boot context loaded ({mode} mode)",
        )
    except Exception as exc:
        logger.warning("Boot context load failed: %s", exc)
        return BootContextResponse(mode=mode, axes={}, summary=f"Error: {exc}")


# PURPOSE: stats を取得する
@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """知識統合層の統計情報を取得。"""
    from mekhane.symploke.sophia_ingest import DEFAULT_INDEX_PATH as SOPHIA_INDEX
    from mekhane.symploke.kairos_ingest import (
        DEFAULT_INDEX_PATH as KAIROS_INDEX,
        HANDOFF_DIR,
    )

    # Handoff 数
    handoff_count = 0
    if HANDOFF_DIR.exists():
        handoff_count = len(list(HANDOFF_DIR.glob("handoff_*.md")))

    # Persona 存在確認
    persona_path = _PROJECT_ROOT / "kernel" / "persona" / "claude_persona.yaml"

    # Boot axes の確認
    boot_axes = []
    try:
        from mekhane.symploke.boot_axes import BOOT_AXES
        boot_axes = list(BOOT_AXES.keys()) if hasattr(BOOT_AXES, 'keys') else []
    except Exception:
        pass

    return StatsResponse(
        handoff_count=handoff_count,
        sophia_index_exists=SOPHIA_INDEX.exists(),
        kairos_index_exists=KAIROS_INDEX.exists(),
        persona_exists=persona_path.exists(),
        boot_axes_available=boot_axes,
    )
