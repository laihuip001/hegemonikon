# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: /api/status/* — システムヘルスチェックエンドポイント
"""
Status Routes — Peira hgk_health モジュールのラッパー

GET /api/status/health  — Tauri ヘルスチェック用 (軽量)
GET /api/status         — 全サービスの詳細レポート
"""

import asyncio
import time
from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

# PURPOSE: レスポンスモデル (/dia+ fix #3: Pydantic models)
class HealthItemResponse(BaseModel):
    """個別ヘルスチェック結果。"""
    name: str
    status: str = Field(description="ok | warn | error | unknown")
    detail: str = ""
    metric: float | None = None
    emoji: str = ""


class HealthReportResponse(BaseModel):
    """全体ヘルスレポート。"""
    timestamp: str
    items: list[HealthItemResponse]
    score: float = Field(ge=0.0, le=1.0, description="0.0-1.0 総合スコア")


class HealthCheckResponse(BaseModel):
    """軽量ヘルスチェック。"""
    status: str = "ok"
    version: str = ""
    uptime_seconds: float = 0.0


# PURPOSE: R3 fix — サーバー起動時刻（app.state 未設定時のフォールバック）
_start_time = time.time()

router = APIRouter(prefix="/status", tags=["status"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(request: Request) -> HealthCheckResponse:
    """Tauri ヘルスチェック用の軽量エンドポイント。"""
    from mekhane.api import __version__
    start = getattr(request.app.state, "start_time", _start_time)
    return HealthCheckResponse(
        status="ok",
        version=__version__,
        uptime_seconds=round(time.time() - start, 1),
    )


@router.get("", response_model=HealthReportResponse)
async def full_status() -> HealthReportResponse:
    """全サービスの詳細ヘルスレポート。

    systemd/docker コマンドを呼ぶため非同期スレッドで実行。
    """
    from mekhane.peira.hgk_health import run_health_check

    # /dia+ fix #3: blocking call を非同期スレッドで実行
    report = await asyncio.to_thread(run_health_check)

    items = [
        HealthItemResponse(
            name=item.name,
            status=item.status,
            detail=item.detail,
            metric=item.metric,
            emoji=item.emoji,
        )
        for item in report.items
    ]

    return HealthReportResponse(
        timestamp=report.timestamp,
        items=items,
        score=report.score,
    )
