#!/usr/bin/env python3
# PROOF: [L2/Gnōsis] <- mekhane/api/routes/
# PURPOSE: Gnōsis Narrator API — 論文カード + 問い + ナレーション
"""
Gnōsis Narrator Routes — 知識は問いとして走ってくる

GET  /api/gnosis/papers     — 論文カード一覧（問いの一行付き）
POST /api/gnosis/narrate    — ナレーション生成（LLM / テンプレート）
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("hegemonikon.api.gnosis")

router = APIRouter(prefix="/gnosis", tags=["gnosis"])


# ===========================================================================
# Pydantic Models
# ===========================================================================

# PURPOSE: PaperCard の機能を提供する
class PaperCard(BaseModel):
    """論文カード — kalon: カード + 問いの一行"""
    title: str
    authors: str = ""
    abstract: str = ""
    source: str = ""
    topics: list[str] = Field(default_factory=list)
    relevance_score: float = 0.0
    question: str = ""   # kalon: この論文が投げかける問い


# PURPOSE: PapersResponse の機能を提供する
class PapersResponse(BaseModel):
    timestamp: str
    papers: list[PaperCard] = Field(default_factory=list)
    total: int = 0


# PURPOSE: NarrateSegment の機能を提供する
class NarrateSegment(BaseModel):
    speaker: str
    content: str


# PURPOSE: NarrateRequest の機能を提供する
class NarrateRequest(BaseModel):
    title: str
    fmt: str = "deep_dive"  # deep_dive / brief / critique / debate


# PURPOSE: NarrateResponse の機能を提供する
class NarrateResponse(BaseModel):
    timestamp: str
    title: str
    fmt: str
    segments: list[NarrateSegment] = Field(default_factory=list)
    icon: str = ""
    generated: bool = False


# ===========================================================================
# Lazy Initialization
# ===========================================================================

_engine = None
_narrator = None


def _get_engine():
    """PKSEngine — 遅延初期化 (ベクトル検索用)"""
    global _engine
    if _engine is None:
        try:
            from mekhane.pks.pks_engine import PKSEngine
            _engine = PKSEngine(enable_feedback=False, enable_questions=False)
            logger.info("PKSEngine initialized for gnosis narrator")
        except Exception as e:
            logger.warning("PKSEngine init failed: %s", e)
    return _engine


def _get_narrator():
    """PKSNarrator — 遅延初期化"""
    global _narrator
    if _narrator is None:
        try:
            from mekhane.pks.narrator import PKSNarrator
            _narrator = PKSNarrator(use_llm=True, model="gemini-2.0-flash")
            logger.info("PKSNarrator initialized (LLM=%s)", _narrator.llm_available)
        except Exception as e:
            logger.warning("PKSNarrator init failed: %s", e)
    return _narrator


def _generate_question(title: str, abstract: str, topics: list[str]) -> str:
    """kalon: 論文から問いを生成（テンプレート）"""
    if topics:
        topic = topics[0]
        templates = [
            f"「{topic}」の前提を疑うと、何が見えてくるか？",
            f"この研究が示す「{topic}」の限界は何か？",
            f"「{topic}」を逆転させたらどうなるか？",
        ]
        # タイトルのハッシュで決定的に選択
        idx = sum(ord(c) for c in title) % len(templates)
        return templates[idx]
    # トピックがない場合
    if len(abstract) > 50:
        return "この知見が覆される条件は何か？"
    return "なぜこの研究が今、重要なのか？"


# ===========================================================================
# Endpoints
# ===========================================================================

# PURPOSE: gnosis_narrator の list papers 処理を実行する
@router.get("/papers", response_model=PapersResponse)
async def list_papers(
    query: str = Query("", description="Search query (empty=recent)"),
    limit: int = Query(20, ge=1, le=100),
) -> PapersResponse:
    """論文カード一覧 — 各カードに「問いの一行」付き"""
    now = datetime.now(timezone.utc)
    engine = _get_engine()
    if not engine:
        return PapersResponse(timestamp=now.isoformat())

    try:
        # KnowledgeNugget として取得
        # NOTE: proactive_push は同期的。軽量なため許容。
        if query:
            from mekhane.pks.pks_engine import KnowledgeNugget
            # search 経由
            nuggets = engine.search(query, k=limit)
        else:
            nuggets = engine.proactive_push(k=limit)

        papers = []
        for n in nuggets:
            topics = getattr(n, "topics", []) or []
            q = _generate_question(n.title, n.abstract or "", topics)
            papers.append(PaperCard(
                title=n.title,
                authors=getattr(n, "authors", "") or "",
                abstract=(n.abstract or "")[:300],
                source=getattr(n, "source", "") or "",
                topics=topics,
                relevance_score=getattr(n, "relevance_score", 0.0) or 0.0,
                question=q,
            ))

        return PapersResponse(
            timestamp=now.isoformat(),
            papers=papers,
            total=len(papers),
        )
    except Exception as e:
        logger.warning("Papers listing failed: %s", e)
        return PapersResponse(timestamp=now.isoformat())


# PURPOSE: gnosis_narrator の narrate 処理を実行する
@router.post("/narrate", response_model=NarrateResponse)
async def narrate(req: NarrateRequest) -> NarrateResponse:
    """論文のナレーション生成（LLM or テンプレート）"""
    now = datetime.now(timezone.utc)
    engine = _get_engine()
    narrator = _get_narrator()

    if not engine or not narrator:
        return NarrateResponse(
            timestamp=now.isoformat(),
            title=req.title,
            fmt=req.fmt,
        )

    try:
        from mekhane.pks.narrator_formats import NarratorFormat, get_format_spec

        fmt = NarratorFormat.from_str(req.fmt)
        spec = get_format_spec(fmt)

        # タイトルで検索して nugget を取得
        nuggets = engine.search(req.title, k=1) if hasattr(engine, 'search') else []
        if not nuggets:
            nuggets = engine.proactive_push(k=5)
            nuggets = [n for n in nuggets if req.title.lower() in n.title.lower()]

        if not nuggets:
            return NarrateResponse(
                timestamp=now.isoformat(),
                title=req.title,
                fmt=req.fmt,
            )

        nugget = nuggets[0]
        narrative = narrator.narrate(nugget, fmt=fmt)

        segments = [
            NarrateSegment(speaker=seg.speaker, content=seg.content)
            for seg in narrative.segments
        ]

        return NarrateResponse(
            timestamp=now.isoformat(),
            title=narrative.title,
            fmt=req.fmt,
            segments=segments,
            icon=spec.icon,
            generated=True,
        )
    except Exception as e:
        logger.warning("Narration failed: %s", e)
        return NarrateResponse(
            timestamp=now.isoformat(),
            title=req.title,
            fmt=req.fmt,
        )
