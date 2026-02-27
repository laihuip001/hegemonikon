#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/api/routes/sentinel.py S2→Mekhane→API
# PROOF: [L2/Sentinel] <- mekhane/api/routes/
# PURPOSE: Paper Sentinel API — 論文スキャン結果の提供
"""
Sentinel Routes — Paper Sentinel レポート API

paper_sentinel.json と sentinel/ レポートを読んで返す。
"""

from __future__ import annotations
import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/sentinel", tags=["sentinel"])

MNEME = Path.home() / "oikos" / "mneme" / ".hegemonikon"
SENTINEL_DIR = MNEME / "sentinel"


@router.get("/latest")
async def sentinel_latest():
    """最新の Sentinel サマリーを返す"""
    path = MNEME / "paper_sentinel.json"
    if not path.exists():
        return {"status": "no_data", "message": "Paper Sentinel has not run yet"}
    
    try:
        data = json.loads(path.read_text("utf-8"))
        return data
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/reports")
async def sentinel_reports(limit: int = 10):
    """Sentinel レポート一覧を返す"""
    if not SENTINEL_DIR.exists():
        return {"reports": [], "total": 0}
    
    files = sorted(SENTINEL_DIR.glob("paper_*.md"), reverse=True)[:limit]
    reports = []
    for f in files:
        reports.append({
            "filename": f.name,
            "date": f.stem.replace("paper_", ""),
            "size_bytes": f.stat().st_size,
        })
    
    return {"reports": reports, "total": len(reports)}


@router.get("/report/{date}")
async def sentinel_report(date: str):
    """特定日のレポート内容を返す"""
    path = SENTINEL_DIR / f"paper_{date}.md"
    if not path.exists():
        return {"status": "not_found", "date": date}
    
    return {
        "date": date,
        "content": path.read_text("utf-8"),
        "size_bytes": path.stat().st_size,
    }
