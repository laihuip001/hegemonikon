#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Basanos — 多視点スキャン (SweepEngine) + L2 構造的差分スキャン REST API
"""
Basanos Routes — SweepEngine + ResponseCache REST API

POST   /api/basanos/sweep         — ファイル指定 sweep 実行
GET    /api/basanos/perspectives   — 利用可能な perspective 一覧
GET    /api/basanos/cache/stats    — ResponseCache 統計
POST   /api/basanos/cache/clear    — キャッシュクリア
"""

import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("hegemonikon.api.basanos")
router = APIRouter(prefix="/basanos", tags=["basanos"])


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


# --- L2 Structural Deficit Scan ---


class L2DeficitItem(BaseModel):
    """L2 で検出された deficit の1件。"""
    type: str  # eta, epsilon-impl, epsilon-just, delta
    severity: float
    source: str
    target: str
    description: str
    suggested_action: str = ""


class L2ScanResponse(BaseModel):
    """L2 構造的差分スキャン結果。"""
    total: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)
    top_deficits: list[L2DeficitItem] = Field(default_factory=list)
    status: str = "ok"  # ok, warn, error
    error: str = ""


@router.get("/l2/scan", response_model=L2ScanResponse)
async def l2_scan():
    """L2 構造的差分スキャンを実行しサマリーを返す。"""
    try:
        from mekhane.basanos.l2.cli import scan_deficits, detect_project_root

        project_root = detect_project_root()
        deficits = scan_deficits(project_root)

        by_type: dict[str, int] = {}
        for d in deficits:
            key = d.type.value if hasattr(d.type, "value") else str(d.type)
            by_type[key] = by_type.get(key, 0) + 1

        top = deficits[:10]
        items = [
            L2DeficitItem(
                type=d.type.value if hasattr(d.type, "value") else str(d.type),
                severity=d.severity,
                source=d.source,
                target=d.target,
                description=d.description,
                suggested_action=d.suggested_action,
            )
            for d in top
        ]

        status = "ok" if len(deficits) == 0 else "warn" if len(deficits) <= 5 else "error"

        return L2ScanResponse(
            total=len(deficits),
            by_type=by_type,
            top_deficits=items,
            status=status,
        )
    except Exception as exc:
        logger.error("L2 scan failed: %s", exc)
        return L2ScanResponse(status="error", error=str(exc))


class L2HistoryRecord(BaseModel):
    """履歴レコード1件。"""
    timestamp: str
    scan_type: str = "full"
    total: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)


class L2HistoryResponse(BaseModel):
    """履歴一覧レスポンス。"""
    records: list[L2HistoryRecord] = Field(default_factory=list)
    count: int = 0


class L2TrendResponse(BaseModel):
    """トレンド分析レスポンス。"""
    direction: str = "unknown"  # improving, worsening, stable
    current: int = 0
    previous: int = 0
    delta: int = 0
    sparkline: str = ""
    window: int = 0


@router.get("/l2/history", response_model=L2HistoryResponse)
async def l2_history(limit: int = 20):
    """L2 deficit スキャン履歴を取得。"""
    try:
        from mekhane.basanos.l2.history import load_history

        records = load_history(limit=limit)
        items = [
            L2HistoryRecord(
                timestamp=r.get("timestamp", ""),
                scan_type=r.get("scan_type", "full"),
                total=r.get("total", 0),
                by_type=r.get("by_type", {}),
            )
            for r in records
        ]
        return L2HistoryResponse(records=items, count=len(items))
    except Exception as exc:
        logger.error("L2 history failed: %s", exc)
        return L2HistoryResponse()


@router.get("/l2/trend", response_model=L2TrendResponse)
async def l2_trend(window: int = 10):
    """L2 deficit トレンドを取得。"""
    try:
        from mekhane.basanos.l2.history import get_trend

        trend = get_trend(window=window)
        return L2TrendResponse(**trend)
    except Exception as exc:
        logger.error("L2 trend failed: %s", exc)
        return L2TrendResponse()


class L2ResolutionItem(BaseModel):
    """解決提案1件。"""
    question: str
    deficit_type: str
    strategy: str
    confidence: float
    actions: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    status: str = "proposed"


class L2ResolveResponse(BaseModel):
    """L3 自動解決レスポンス。"""
    resolutions: list[L2ResolutionItem] = Field(default_factory=list)
    total: int = 0
    error: str = ""


@router.get("/l2/resolve", response_model=L2ResolveResponse)
async def l2_resolve(limit: int = 5):
    """L3 自動解決ループ: deficit→問い→解決策を返す。"""
    try:
        from mekhane.basanos.l2.cli import scan_deficits, detect_project_root
        from mekhane.basanos.l2.resolver import Resolver

        project_root = detect_project_root()
        deficits = scan_deficits(project_root)
        resolver = Resolver(project_root)
        resolutions = resolver.resolve_batch(deficits, max_resolutions=limit)

        items = [
            L2ResolutionItem(
                question=r.question.text,
                deficit_type=r.question.deficit.type.value,
                strategy=r.strategy,
                confidence=r.confidence,
                actions=r.actions,
                references=[str(ref) for ref in r.references],
                status=r.status,
            )
            for r in resolutions
        ]
        return L2ResolveResponse(resolutions=items, total=len(items))
    except Exception as exc:
        logger.error("L2 resolve failed: %s", exc)
        return L2ResolveResponse(error=str(exc))
