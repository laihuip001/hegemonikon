#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Synedrion (SweepEngine) — 多視点プロンプトスキャン REST API
"""
Synedrion Routes — SweepEngine + ResponseCache REST API

POST   /api/synedrion/sweep         — ファイル指定 sweep 実行
GET    /api/synedrion/perspectives   — 利用可能な perspective 一覧
GET    /api/synedrion/cache/stats    — ResponseCache 統計
POST   /api/synedrion/cache/clear    — キャッシュクリア
"""

import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("hegemonikon.api.synedrion")
router = APIRouter(prefix="/synedrion", tags=["synedrion"])


# --- Pydantic Models ---


class SweepRequest(BaseModel):
    """Sweep スキャンリクエスト。"""
    filepath: str = Field(..., description="スキャン対象ファイルパス")
    domains: Optional[list[str]] = Field(
        default=None, description="ドメインフィルタ (Security, Performance, ...)"
    )
    axes: Optional[list[str]] = Field(
        default=None, description="座標フィルタ (O1, O2, ...)"
    )
    max_perspectives: int = Field(default=10, ge=1, le=50, description="最大 perspective 数")
    model: str = Field(default="gemini-2.0-flash", description="使用モデル")


class SweepIssueResponse(BaseModel):
    """検出された1件の issue。"""
    perspective_id: str
    domain: str
    axis: str
    severity: str
    description: str
    recommendation: str = ""


class SweepResultResponse(BaseModel):
    """Sweep スキャン結果。"""
    filepath: str
    issue_count: int
    issues: list[SweepIssueResponse] = Field(default_factory=list)
    severity: dict[str, int] = Field(default_factory=dict)
    silences: int = 0
    errors: int = 0
    total_perspectives: int = 0
    coverage: float = 0.0
    elapsed_seconds: float = 0.0


class PerspectiveInfo(BaseModel):
    """利用可能な perspective 情報。"""
    id: str
    domain: str
    axis: str
    system_instruction: str = ""


class CacheStatsResponse(BaseModel):
    """ResponseCache 統計。"""
    total_entries: int = 0
    size_mb: float = 0.0
    hits: int = 0
    misses: int = 0
    hit_rate: float = 0.0
    oldest_age_hours: float = 0.0
    ttl_seconds: int = 0
    max_size_mb: float = 0.0


class CacheClearResponse(BaseModel):
    """キャッシュクリア結果。"""
    cleared: int = 0
    message: str = ""


# --- Routes ---


@router.post("/sweep", response_model=SweepResultResponse)
async def sweep(request: SweepRequest):
    """ファイルを指定して多視点 sweep スキャンを実行。"""
    try:
        from mekhane.ergasterion.tekhne.sweep_engine import SweepEngine

        # Path validation
        filepath = Path(request.filepath).resolve()
        if not filepath.is_file():
            raise HTTPException(status_code=400, detail=f"File not found: {request.filepath}")

        engine = SweepEngine(model=request.model, use_cache=True)
        report = engine.sweep(
            filepath=str(filepath),
            max_perspectives=request.max_perspectives,
            domains=request.domains,
            axes=request.axes,
        )

        issues = [
            SweepIssueResponse(
                perspective_id=i.perspective_id,
                domain=i.domain,
                axis=i.axis,
                severity=i.severity,
                description=i.description,
                recommendation=i.recommendation,
            )
            for i in report.issues
        ]

        return SweepResultResponse(
            filepath=str(filepath),
            issue_count=report.issue_count,
            issues=issues,
            severity=report.by_severity(),
            silences=report.silences,
            errors=report.errors,
            total_perspectives=report.total_perspectives,
            coverage=report.coverage,
            elapsed_seconds=report.elapsed_seconds,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Sweep failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Sweep failed: {exc}")


@router.get("/perspectives", response_model=list[PerspectiveInfo])
async def list_perspectives():
    """利用可能な perspective の一覧を取得。"""
    try:
        from mekhane.ergasterion.tekhne.sweep_engine import SweepEngine

        engine = SweepEngine()
        perspectives = engine._generate_perspectives(max_count=50)

        return [
            PerspectiveInfo(
                id=p["id"],
                domain=p["domain"],
                axis=p["axis"],
                system_instruction=p.get("system_instruction", "")[:200],
            )
            for p in perspectives
        ]
    except Exception as exc:
        logger.error("Perspectives list failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed: {exc}")


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def cache_stats():
    """ResponseCache の統計情報を取得。"""
    try:
        from mekhane.ergasterion.tekhne.response_cache import (
            ResponseCache, DEFAULT_TTL, MAX_CACHE_SIZE_MB,
        )

        cache = ResponseCache()
        stats = cache.stats()

        # TTL override from env
        env_ttl = os.getenv("HGK_CACHE_TTL")
        ttl = int(env_ttl) if env_ttl else DEFAULT_TTL

        return CacheStatsResponse(
            total_entries=stats.total_entries,
            size_mb=stats.size_mb,
            hits=stats.hits,
            misses=stats.misses,
            hit_rate=stats.hit_rate,
            oldest_age_hours=stats.oldest_age_hours,
            ttl_seconds=ttl,
            max_size_mb=MAX_CACHE_SIZE_MB,
        )
    except Exception as exc:
        logger.error("Cache stats failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Cache stats failed: {exc}")


@router.post("/cache/clear", response_model=CacheClearResponse)
async def cache_clear():
    """ResponseCache をクリアする。"""
    try:
        from mekhane.ergasterion.tekhne.response_cache import ResponseCache

        cache = ResponseCache()
        cleared = cache.clear()

        return CacheClearResponse(
            cleared=cleared,
            message=f"{cleared} entries cleared",
        )
    except Exception as exc:
        logger.error("Cache clear failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {exc}")
