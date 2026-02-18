#!/usr/bin/env python3
# PROOF: [L2/Periskopē] <- mekhane/api/routes/
# PURPOSE: Periskopē Research API — 研究結果の提供・非同期リクエスト
"""
Periskopē Routes — 研究エンジン API

最新研究レポート、研究履歴、非同期研究リクエストを提供。
"""

from __future__ import annotations
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(prefix="/periskope", tags=["periskope"])

logger = logging.getLogger("hegemonikon.api.periskope")

MNEME = Path.home() / "oikos" / "mneme" / ".hegemonikon"
INCOMING_DIR = MNEME / "incoming"
REPORTS_DIR = MNEME / "periskope"


class ResearchRequest(BaseModel):
    """非同期研究リクエスト"""
    query: str
    sources: list[str] | None = None
    auto_digest: bool = False
    digest_depth: str = "quick"


@router.get("/status")
async def periskope_status():
    """Periskopē エンジンのステータスサマリー"""
    # Count digest files
    digest_count = 0
    if INCOMING_DIR.exists():
        digest_count = len(list(INCOMING_DIR.glob("eat_*_periskope_*.md")))

    # Count report files
    report_count = 0
    latest_report = None
    if REPORTS_DIR.exists():
        reports = sorted(REPORTS_DIR.glob("report_*.json"), reverse=True)
        report_count = len(reports)
        if reports:
            try:
                latest_report = json.loads(reports[0].read_text("utf-8"))
            except Exception:
                latest_report = {"filename": reports[0].name}

    return {
        "status": "ready",
        "digest_pending": digest_count,
        "total_reports": report_count,
        "latest": latest_report,
    }


@router.get("/history")
async def periskope_history(limit: int = 20):
    """過去の研究レポート一覧"""
    if not REPORTS_DIR.exists():
        return {"reports": [], "total": 0}

    files = sorted(REPORTS_DIR.glob("report_*.json"), reverse=True)[:limit]
    reports = []
    for f in files:
        try:
            data = json.loads(f.read_text("utf-8"))
            reports.append({
                "filename": f.name,
                "query": data.get("query", ""),
                "confidence": data.get("confidence", 0),
                "elapsed": data.get("elapsed_seconds", 0),
                "date": f.stem.replace("report_", ""),
                "size_bytes": f.stat().st_size,
            })
        except Exception:
            reports.append({
                "filename": f.name,
                "date": f.stem.replace("report_", ""),
                "size_bytes": f.stat().st_size,
            })

    return {"reports": reports, "total": len(reports)}


@router.get("/report/{filename}")
async def periskope_report(filename: str):
    """特定レポートの内容を返す"""
    path = REPORTS_DIR / filename
    if not path.exists():
        return {"status": "not_found", "filename": filename}

    try:
        data = json.loads(path.read_text("utf-8"))
        return data
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/research")
async def periskope_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
):
    """非同期研究リクエスト (バックグラウンド実行)"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"report_{timestamp}.json"

    background_tasks.add_task(
        _run_research,
        query=request.query,
        sources=request.sources,
        auto_digest=request.auto_digest,
        digest_depth=request.digest_depth,
        report_path=report_path,
    )

    return {
        "status": "accepted",
        "query": request.query,
        "report_path": str(report_path),
        "message": "Research started in background",
    }


async def _run_research(
    query: str,
    sources: list[str] | None,
    auto_digest: bool,
    digest_depth: str,
    report_path: Path,
) -> None:
    """バックグラウンドで研究を実行し、結果を JSON に保存"""
    try:
        from mekhane.periskope.engine import PeriskopeEngine

        engine = PeriskopeEngine()
        report = await engine.research(
            query=query,
            sources=sources,
            auto_digest=auto_digest,
            digest_depth=digest_depth,
        )

        # Serialize to JSON
        result = {
            "query": report.query,
            "elapsed_seconds": report.elapsed_seconds,
            "source_counts": report.source_counts,
            "synthesis_count": len(report.synthesis),
            "citation_count": len(report.citations),
            "confidence": max((s.confidence for s in report.synthesis), default=0),
            "search_result_count": len(report.search_results),
            "timestamp": datetime.now().isoformat(),
        }

        # Add synthesis summaries
        if report.synthesis:
            result["synthesis"] = [
                {
                    "model": s.model.value,
                    "confidence": s.confidence,
                    "content_length": len(s.content),
                    "content_preview": s.content[:500],
                }
                for s in report.synthesis
            ]

        report_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Research report saved: %s", report_path)

    except Exception as e:
        logger.error("Background research failed: %s", e)
        error_result = {
            "query": query,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
        report_path.write_text(
            json.dumps(error_result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
