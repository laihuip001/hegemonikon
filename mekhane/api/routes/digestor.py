#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/ Digestor 候補閲覧 API
"""
Digestor API — digest_report の閲覧エンドポイント

Desktop App から Digestor 候補レポートを閲覧する。
scheduler が生成した digest_report_*.json を読み取ってフロントに返す。
"""

import glob
import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/digestor", tags=["digestor"])

# ─── Constants ────────────────────────────────────────────
DIGESTOR_DIR = Path.home() / ".hegemonikon" / "digestor"


# ─── Models ───────────────────────────────────────────────
class DigestCandidate(BaseModel):
    """Digestor 候補1件"""
    title: str
    source: str = ""
    url: str = ""
    score: float = 0.0
    matched_topics: list[str] = []
    rationale: str = ""
    suggested_templates: list[dict] = []


class DigestReport(BaseModel):
    """Digestor レポート1件"""
    timestamp: str
    source: str = "gnosis"
    total_papers: int = 0
    candidates_selected: int = 0
    dry_run: bool = True
    candidates: list[DigestCandidate] = []
    filename: str = ""


class DigestReportListResponse(BaseModel):
    """レポート一覧レスポンス"""
    reports: list[DigestReport]
    total: int


# ─── Helpers ──────────────────────────────────────────────
def _load_report(fpath: str) -> Optional[DigestReport]:
    """JSON ファイルから DigestReport を生成。失敗時は None。"""
    try:
        with open(fpath) as f:
            data = json.load(f)
        return DigestReport(
            timestamp=data.get("timestamp", ""),
            source=data.get("source", "gnosis"),
            total_papers=data.get("total_papers", 0),
            candidates_selected=data.get("candidates_selected", 0),
            dry_run=data.get("dry_run", True),
            candidates=[
                DigestCandidate(**c) for c in data.get("candidates", [])
            ],
            filename=Path(fpath).name,
        )
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Failed to load digest report %s: %s", fpath, exc)
        return None


def _list_report_files() -> list[str]:
    """digest_report_*.json を新しい順に返す。"""
    pattern = str(DIGESTOR_DIR / "digest_report_*.json")
    return sorted(glob.glob(pattern), reverse=True)


# ─── Endpoints ────────────────────────────────────────────
@router.get("/reports", response_model=DigestReportListResponse)
async def list_reports(
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
) -> DigestReportListResponse:
    """digest_report 一覧を取得（新しい順）"""
    files = _list_report_files()
    total = len(files)
    page = files[offset:offset + limit]

    reports: list[DigestReport] = []
    for fpath in page:
        report = _load_report(fpath)
        if report is not None:
            reports.append(report)

    return DigestReportListResponse(reports=reports, total=total)


@router.get("/latest", response_model=Optional[DigestReport])
async def latest_report() -> Optional[DigestReport]:
    """最新のレポートを取得"""
    files = _list_report_files()
    if not files:
        return None
    return _load_report(files[0])


# ─── Run Pipeline ─────────────────────────────────────────
class RunRequest(BaseModel):
    """パイプライン実行リクエスト"""
    max_papers: int = 30
    max_candidates: int = 10
    dry_run: bool = False
    topics: Optional[list[str]] = None


class RunResponse(BaseModel):
    """パイプライン実行レスポンス"""
    success: bool
    timestamp: str = ""
    total_papers: int = 0
    candidates_selected: int = 0
    candidates: list[DigestCandidate] = []
    error: str = ""


@router.post("/run", response_model=RunResponse)
async def run_pipeline(req: RunRequest = RunRequest()) -> RunResponse:
    """Digestor パイプラインを実行（n8n Schedule Trigger 用）"""
    try:
        from mekhane.ergasterion.digestor.pipeline import DigestorPipeline

        pipeline = DigestorPipeline()
        result = pipeline.run(
            topics=req.topics,
            max_papers=req.max_papers,
            max_candidates=req.max_candidates,
            dry_run=req.dry_run,
        )

        candidates = []
        for c in result.candidates:
            candidates.append(DigestCandidate(
                title=c.paper.title,
                source=c.paper.source,
                url=c.paper.url or "",
                score=c.score,
                matched_topics=c.matched_topics,
                rationale=getattr(c, 'rationale', ''),
            ))

        return RunResponse(
            success=True,
            timestamp=result.timestamp,
            total_papers=result.total_papers,
            candidates_selected=result.candidates_selected,
            candidates=candidates,
        )
    except Exception as exc:
        logger.error("Digestor pipeline failed: %s", exc)
        return RunResponse(success=False, error=str(exc))
