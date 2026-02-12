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
    """
    Represents a single digest candidate.

    Attributes:
        title: The title of the digest item.
        source: The source origin (e.g., 'gnosis').
        url: The URL to the original content.
        score: The relevance score of the candidate.
        matched_topics: List of topics that matched this candidate.
        rationale: Explanation for why this candidate was selected.
        suggested_templates: List of suggested templates for processing.
    """

    title: str
    source: str = ""
    url: str = ""
    score: float = 0.0
    matched_topics: list[str] = []
    rationale: str = ""
    suggested_templates: list[dict] = []


class DigestReport(BaseModel):
    """
    Represents a full digest report containing multiple candidates.

    Attributes:
        timestamp: The creation timestamp of the report.
        source: The source origin of the report.
        total_papers: Total number of papers processed.
        candidates_selected: Number of candidates selected for the report.
        dry_run: Whether the report was generated in dry-run mode.
        candidates: List of selected candidates.
        filename: The filename of the report source.
    """

    timestamp: str
    source: str = "gnosis"
    total_papers: int = 0
    candidates_selected: int = 0
    dry_run: bool = True
    candidates: list[DigestCandidate] = []
    filename: str = ""


class DigestReportListResponse(BaseModel):
    """
    Response model for listing digest reports.

    Attributes:
        reports: List of digest reports in the current page.
        total: Total number of reports available.
    """

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
    """
    Retrieve a list of digest reports.

    Fetches the list of available digest reports, sorted by creation date (newest first).

    Args:
        limit: Maximum number of reports to return (default: 10).
        offset: Number of reports to skip (default: 0).

    Returns:
        DigestReportListResponse containing the list of reports and total count.
    """
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
    """
    Retrieve the latest digest report.

    Fetches the most recently created digest report.

    Returns:
        The latest DigestReport if available, or None if no reports exist.
    """
    files = _list_report_files()
    if not files:
        return None
    return _load_report(files[0])
