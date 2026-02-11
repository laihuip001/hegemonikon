#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/ Digestor 候補閲覧 API
"""
Digestor API — digest_report の閲覧エンドポイント

Desktop App から Digestor 候補レポートを閲覧する。
scheduler が生成した digest_report_*.json を読み取ってフロントに返す。
"""

import glob
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/digestor", tags=["digestor"])

# ─── Constants ────────────────────────────────────────────
DIGESTOR_DIR = Path.home() / ".hegemonikon" / "digestor"


# ─── Models ───────────────────────────────────────────────
# PURPOSE: DigestCandidate の機能を提供する
class DigestCandidate(BaseModel):
    """候補1件"""
    title: str
    source: str = ""
    url: str = ""
    score: float = 0.0
    matched_topics: list[str] = []
    rationale: str = ""
    suggested_templates: list[dict] = []


# PURPOSE: DigestReport の機能を提供する
class DigestReport(BaseModel):
    """1つのレポート"""
    timestamp: str
    source: str = "gnosis"
    total_papers: int = 0
    candidates_selected: int = 0
    dry_run: bool = True
    candidates: list[DigestCandidate] = []
    filename: str = ""


# PURPOSE: DigestReportListResponse の機能を提供する
class DigestReportListResponse(BaseModel):
    """レポート一覧"""
    reports: list[DigestReport]
    total: int


# ─── Endpoints ────────────────────────────────────────────
# PURPOSE: digestor の list reports 処理を実行する
@router.get("/reports", response_model=DigestReportListResponse)
async def list_reports(
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
) -> DigestReportListResponse:
    """digest_report 一覧を取得（新しい順）"""
    pattern = str(DIGESTOR_DIR / "digest_report_*.json")
    files = sorted(glob.glob(pattern), reverse=True)  # newest first
    total = len(files)
    page = files[offset:offset + limit]

    reports = []
    for fpath in page:
        try:
            with open(fpath) as f:
                data = json.load(f)
            report = DigestReport(
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
            reports.append(report)
        except (json.JSONDecodeError, KeyError):
            continue

    return DigestReportListResponse(reports=reports, total=total)


# PURPOSE: digestor の latest report 処理を実行する
@router.get("/latest", response_model=Optional[DigestReport])
async def latest_report() -> Optional[DigestReport]:
    """最新のレポートを取得"""
    pattern = str(DIGESTOR_DIR / "digest_report_*.json")
    files = sorted(glob.glob(pattern), reverse=True)
    if not files:
        return None

    try:
        with open(files[0]) as f:
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
            filename=Path(files[0]).name,
        )
    except (json.JSONDecodeError, KeyError):
        return None
