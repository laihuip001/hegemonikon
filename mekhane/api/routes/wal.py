#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/routes/ A0->Auto->AddedByCI
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Intent-WAL ダッシュボードカード API — WAL ステータス・履歴の閲覧
"""
Intent-WAL Dashboard API

セッション意図ログ (WAL) の現在状態と履歴を REST API として公開する。
ダッシュボードの WAL カードで消費される。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

logger = logging.getLogger("hegemonikon.api.wal")

router = APIRouter(tags=["wal"])

# WAL ディレクトリ
_MNEME_DIR = Path.home() / "oikos" / "mneme" / ".hegemonikon"
_WAL_DIR = _MNEME_DIR / "wal"


# --- Response Models ---

class WALEntry(BaseModel):
    """個別 WAL エントリ"""
    filename: str
    session_id: str
    goal: str
    status: str  # active, completed, abandoned
    progress: list[str]
    created: str  # ISO 8601


class WALStatusResponse(BaseModel):
    """WAL ステータス概要"""
    total_wals: int
    active_wals: int
    latest: Optional[WALEntry] = None
    recent: list[WALEntry]


class WALDetailResponse(BaseModel):
    """WAL 詳細"""
    entry: WALEntry
    raw_content: str


# --- Helpers ---

def _parse_wal_file(path: Path) -> Optional[WALEntry]:
    """YAML WAL ファイルをパースする。"""
    try:
        import yaml
        content = path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            return None

        return WALEntry(
            filename=path.name,
            session_id=data.get("session_id", "unknown"),
            goal=data.get("goal", ""),
            status=data.get("status", "unknown"),
            progress=data.get("progress", []),
            created=data.get("created", path.stat().st_mtime.__str__()),
        )
    except Exception as exc:
        logger.warning("Failed to parse WAL %s: %s", path.name, exc)
        return None


def _scan_wals(limit: int = 20) -> list[WALEntry]:
    """WAL ディレクトリをスキャンしてエントリ一覧を返す。"""
    if not _WAL_DIR.exists():
        return []

    entries: list[WALEntry] = []
    wal_files = sorted(
        _WAL_DIR.glob("intent_wal_*.yaml"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for path in wal_files[:limit]:
        entry = _parse_wal_file(path)
        if entry:
            entries.append(entry)

    return entries


# --- Endpoints ---

@router.get("/wal/status", response_model=WALStatusResponse)
async def wal_status():
    """WAL ステータス概要を返す (ダッシュボードカード用)。"""
    entries = _scan_wals(limit=10)
    active = [e for e in entries if e.status == "active"]

    return WALStatusResponse(
        total_wals=len(list(_WAL_DIR.glob("intent_wal_*.yaml"))) if _WAL_DIR.exists() else 0,
        active_wals=len(active),
        latest=entries[0] if entries else None,
        recent=entries[:5],
    )


@router.get("/wal/history", response_model=list[WALEntry])
async def wal_history(
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(active|completed|abandoned)$"),
):
    """WAL 履歴を返す。status でフィルタ可能。"""
    entries = _scan_wals(limit=limit)
    if status:
        entries = [e for e in entries if e.status == status]
    return entries


@router.get("/wal/{filename}", response_model=WALDetailResponse)
async def wal_detail(filename: str):
    """個別 WAL ファイルの詳細を返す。"""
    from fastapi import HTTPException

    path = _WAL_DIR / filename
    if not path.exists() or not path.name.startswith("intent_wal_"):
        raise HTTPException(status_code=404, detail=f"WAL not found: {filename}")

    entry = _parse_wal_file(path)
    if not entry:
        raise HTTPException(status_code=500, detail=f"Failed to parse WAL: {filename}")

    return WALDetailResponse(
        entry=entry,
        raw_content=path.read_text(encoding="utf-8"),
    )
