#!/usr/bin/env python3
# PROOF: [L2/PKS] <- mekhane/api/routes/
# PURPOSE: PKS (Proactive Knowledge Surface) API — 知識プッシュ + フィードバック
"""
PKS Routes — 能動的知識表面化 API

GET  /api/pks/push        — 最新の PKS auto-push 結果を取得
POST /api/pks/push        — PKS auto-push を実行
POST /api/pks/feedback    — フィードバック記録 (used/dismissed/deepened)
GET  /api/pks/stats       — フィードバック統計
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("hegemonikon.api.pks")

router = APIRouter(prefix="/pks", tags=["pks"])


# ===========================================================================
# Pydantic Models
# ===========================================================================

# PURPOSE: の統一的インターフェースを実現する
class NuggetResponse(BaseModel):
    title: str
    abstract: str = ""
    source: str = ""
    relevance_score: float = 0.0
    url: str = ""
    authors: str = ""
    push_reason: str = ""
    serendipity_score: float = 0.0
    suggested_questions: list[str] = Field(default_factory=list)


# PURPOSE: の統一的インターフェースを実現する
class PushResponse(BaseModel):
    timestamp: str
    topics: list[str] = Field(default_factory=list)
    nuggets: list[NuggetResponse] = Field(default_factory=list)
    total: int = 0


# PURPOSE: の統一的インターフェースを実現する
class FeedbackRequest(BaseModel):
    title: str
    reaction: str  # used | dismissed | deepened | ignored
    series: str = ""


# PURPOSE: の統一的インターフェースを実現する
class FeedbackResponse(BaseModel):
    timestamp: str
    title: str
    reaction: str
    recorded: bool = True


# PURPOSE: の統一的インターフェースを実現する
class FeedbackStatsResponse(BaseModel):
    timestamp: str
    series_stats: dict = Field(default_factory=dict)
    total_feedbacks: int = 0


# ===========================================================================
# Lazy PKSEngine
# ===========================================================================

_engine = None


def _get_engine():
    """PKSEngine の遅延初期化。埋め込みモデルのロードが重いため。"""
    global _engine
    if _engine is None:
        try:
            from mekhane.pks.pks_engine import PKSEngine
            _engine = PKSEngine(
                enable_questions=False,
                enable_serendipity=True,
                enable_feedback=True,
            )
            logger.info("PKSEngine initialized")
        except Exception as e:
            logger.warning("PKSEngine init failed: %s", e)
    return _engine


# ===========================================================================
# Auto Push
# ===========================================================================

# 最新のプッシュ結果をキャッシュ
_last_push: Optional[PushResponse] = None


# PURPOSE: push を取得する
@router.get("/push", response_model=PushResponse)
async def get_push() -> PushResponse:
    """最新の PKS auto-push 結果を返す。"""
    if _last_push:
        return _last_push
    return PushResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        topics=[],
        nuggets=[],
        total=0,
    )


# PURPOSE: push を実行する
@router.post("/push", response_model=PushResponse)
async def run_push(k: int = Query(20, ge=1, le=100)) -> PushResponse:
    """PKS auto-push を実行し、結果を返す。"""
    global _last_push
    now = datetime.now(timezone.utc)

    engine = _get_engine()
    if not engine:
        return PushResponse(timestamp=now.isoformat())

    # NOTE: PKSEngine のメソッドは同期的。FastAPI の async 内でブロックする可能性がある。
    # 現時点ではモデルロード以外のブロッキングは軽微なため許容。
    # 将来的に重くなる場合は asyncio.to_thread() でラップすること。

    # Handoff からトピック抽出
    topics = engine.auto_context_from_handoff()
    if not topics:
        _last_push = PushResponse(timestamp=now.isoformat(), topics=[], nuggets=[], total=0)
        return _last_push

    # プッシュ実行
    nuggets = engine.proactive_push(k=k)
    nugget_responses = [
        NuggetResponse(
            title=n.title,
            abstract=n.abstract[:500] if n.abstract else "",
            source=n.source,
            relevance_score=n.relevance_score,
            url=n.url or "",
            authors=n.authors or "",
            push_reason=n.push_reason or "",
            serendipity_score=n.serendipity_score,
            suggested_questions=n.suggested_questions or [],
        )
        for n in nuggets
    ]

    _last_push = PushResponse(
        timestamp=now.isoformat(),
        topics=topics,
        nuggets=nugget_responses,
        total=len(nugget_responses),
    )
    return _last_push


# ===========================================================================
# Feedback
# ===========================================================================

# PURPOSE: pks の record feedback 処理を実行する
@router.post("/feedback", response_model=FeedbackResponse)
async def record_feedback(req: FeedbackRequest) -> FeedbackResponse:
    """フィードバックを記録する。"""
    now = datetime.now(timezone.utc)

    engine = _get_engine()
    if not engine:
        logger.warning("Feedback skipped: PKSEngine not available")
        return FeedbackResponse(
            timestamp=now.isoformat(),
            title=req.title,
            reaction=req.reaction,
            recorded=False,
        )

    try:
        engine.record_feedback(
            nugget_title=req.title,
            reaction=req.reaction,
            series=req.series,
        )
    except Exception as e:
        logger.warning("Feedback recording failed: %s", e)
        return FeedbackResponse(
            timestamp=now.isoformat(),
            title=req.title,
            reaction=req.reaction,
            recorded=False,
        )

    return FeedbackResponse(
        timestamp=now.isoformat(),
        title=req.title,
        reaction=req.reaction,
        recorded=True,
    )


# PURPOSE: pks の feedback stats 処理を実行する
@router.get("/stats", response_model=FeedbackStatsResponse)
async def feedback_stats() -> FeedbackStatsResponse:
    """フィードバック統計を返す。"""
    now = datetime.now(timezone.utc)
    engine = _get_engine()

    if engine and engine._feedback:
        try:
            stats = engine._feedback.get_stats()
            total = sum(s.get("count", 0) for s in stats.values()) if stats else 0
            return FeedbackStatsResponse(
                timestamp=now.isoformat(),
                series_stats=stats or {},
                total_feedbacks=total,
            )
        except Exception as e:
            logger.warning("Feedback stats failed: %s", e)

    return FeedbackStatsResponse(timestamp=now.isoformat())
