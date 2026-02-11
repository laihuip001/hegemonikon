#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: セッション・タイムライン API — Handoff, Doxa, WF 実行結果の時系列閲覧
"""
Timeline Router — mneme/ の記録を統合タイムラインとして提供

エンドポイント:
  GET  /timeline/events  — 統合イベントリスト (Handoff + Doxa + WF)
  GET  /timeline/event/{event_id}  — 個別イベントの全文
  GET  /timeline/stats   — 統計情報
"""

from __future__ import annotations

import hashlib
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)

router = APIRouter(tags=["timeline"])

# --- Paths ---
_MNEME_DIR = Path.home() / "oikos" / "mneme" / ".hegemonikon"
_SESSIONS_DIR = _MNEME_DIR / "sessions"
_DOXA_DIR = _MNEME_DIR / "doxa"
_WORKFLOWS_DIR = _MNEME_DIR / "workflows"


def _file_id(path: Path) -> str:
    """ファイルパスから安定した短い ID を生成する。"""
    return hashlib.md5(str(path).encode()).hexdigest()[:12]


def _extract_date(filename: str) -> str | None:
    """ファイル名から日付を抽出する。複数フォーマットに対応。"""
    # handoff_2026-02-11_0940.md → 2026-02-11
    # bou_kalon_next_2026-02-11.md → 2026-02-11
    # 72_derivatives_reference_20260129.md → 2026-01-29
    patterns = [
        r"(\d{4}-\d{2}-\d{2})",      # 2026-02-11
        r"(\d{4})(\d{2})(\d{2})",     # 20260129
    ]
    for pat in patterns:
        m = re.search(pat, filename)
        if m:
            groups = m.groups()
            if len(groups) == 1:
                return groups[0]
            elif len(groups) == 3:
                return f"{groups[0]}-{groups[1]}-{groups[2]}"
    return None


def _extract_title(content: str, filename: str) -> str:
    """Markdown コンテンツからタイトルを抽出する。"""
    for line in content.split("\n")[:10]:
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    # タイトル行がない場合はファイル名を使う
    return filename.replace("_", " ").replace(".md", "").replace(".yaml", "")


def _extract_summary(content: str, max_length: int = 250) -> str:
    """最初の意味のある段落をサマリーとして抽出する。"""
    lines = content.split("\n")
    summary_lines = []
    in_frontmatter = False
    started = False

    for line in lines:
        stripped = line.strip()
        # YAML frontmatter をスキップ
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        # 見出し行をスキップ
        if stripped.startswith("#"):
            if started:
                break  # 2番目の見出しで終了
            continue
        # 空行
        if not stripped:
            if started and summary_lines:
                break
            continue
        # ブロック引用から内容抽出
        if stripped.startswith("> "):
            stripped = stripped[2:]
        started = True
        summary_lines.append(stripped)

    summary = " ".join(summary_lines)
    if len(summary) > max_length:
        summary = summary[:max_length] + "..."
    return summary


def _scan_events(event_type: str | None = None) -> list[dict[str, Any]]:
    """mneme/ ディレクトリをスキャンしてイベントリストを構築する。"""
    events: list[dict[str, Any]] = []

    # 1. Handoff
    if event_type in (None, "handoff") and _SESSIONS_DIR.exists():
        for f in _SESSIONS_DIR.glob("handoff_*.md"):
            try:
                content = f.read_text(encoding="utf-8")
                date = _extract_date(f.name)
                events.append({
                    "id": _file_id(f),
                    "type": "handoff",
                    "title": _extract_title(content, f.name),
                    "date": date or "",
                    "summary": _extract_summary(content),
                    "filename": f.name,
                    "size_bytes": f.stat().st_size,
                    "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                })
            except Exception as e:
                logger.warning("Failed to read %s: %s", f, e)

    # 2. Doxa
    if event_type in (None, "doxa") and _DOXA_DIR.exists():
        for f in sorted(_DOXA_DIR.iterdir()):
            if f.suffix in (".md", ".yaml", ".json"):
                try:
                    content = f.read_text(encoding="utf-8")
                    date = _extract_date(f.name)
                    events.append({
                        "id": _file_id(f),
                        "type": "doxa",
                        "title": _extract_title(content, f.name),
                        "date": date or "",
                        "summary": _extract_summary(content),
                        "filename": f.name,
                        "size_bytes": f.stat().st_size,
                        "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                    })
                except Exception as e:
                    logger.warning("Failed to read %s: %s", f, e)

    # 3. Workflow results
    if event_type in (None, "workflow") and _WORKFLOWS_DIR.exists():
        for f in _WORKFLOWS_DIR.glob("*.md"):
            try:
                content = f.read_text(encoding="utf-8")
                date = _extract_date(f.name)
                events.append({
                    "id": _file_id(f),
                    "type": "workflow",
                    "title": _extract_title(content, f.name),
                    "date": date or "",
                    "summary": _extract_summary(content),
                    "filename": f.name,
                    "size_bytes": f.stat().st_size,
                    "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                })
            except Exception as e:
                logger.warning("Failed to read %s: %s", f, e)

    # mtime で降順ソート (最新が先)
    events.sort(key=lambda e: e.get("mtime", ""), reverse=True)
    return events


# --- ID からファイルパスを逆引き ---
def _find_file_by_id(event_id: str) -> Path | None:
    """event_id からファイルパスを逆引きする。"""
    dirs = [_SESSIONS_DIR, _DOXA_DIR, _WORKFLOWS_DIR]
    for d in dirs:
        if not d.exists():
            continue
        for f in d.iterdir():
            if _file_id(f) == event_id:
                return f
    return None


# --- Endpoints ---

@router.get("/timeline/events")
async def timeline_events(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    event_type: str | None = Query(None, regex="^(handoff|doxa|workflow)$"),
) -> dict[str, Any]:
    """統合タイムラインイベントを返す。"""
    all_events = _scan_events(event_type)
    total = len(all_events)
    page = all_events[offset:offset + limit]

    return {
        "events": page,
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": offset + limit < total,
    }


@router.get("/timeline/event/{event_id}")
async def timeline_event_detail(event_id: str) -> dict[str, Any]:
    """個別イベントの全文コンテンツを返す。"""
    path = _find_file_by_id(event_id)
    if path is None:
        raise HTTPException(status_code=404, detail=f"Event not found: {event_id}")

    content = path.read_text(encoding="utf-8")
    date = _extract_date(path.name)

    # タイプ判定
    if path.parent == _SESSIONS_DIR:
        event_type = "handoff"
    elif path.parent == _DOXA_DIR:
        event_type = "doxa"
    else:
        event_type = "workflow"

    return {
        "id": event_id,
        "type": event_type,
        "title": _extract_title(content, path.name),
        "date": date or "",
        "summary": _extract_summary(content),
        "content": content,
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "mtime": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
    }


@router.get("/timeline/stats")
async def timeline_stats() -> dict[str, Any]:
    """タイムラインの統計情報を返す。"""
    handoff_count = len(list(_SESSIONS_DIR.glob("handoff_*.md"))) if _SESSIONS_DIR.exists() else 0
    doxa_count = len(list(_DOXA_DIR.iterdir())) if _DOXA_DIR.exists() else 0
    wf_count = len(list(_WORKFLOWS_DIR.glob("*.md"))) if _WORKFLOWS_DIR.exists() else 0

    # 最新の Handoff
    latest_handoff = None
    if _SESSIONS_DIR.exists():
        handoffs = sorted(_SESSIONS_DIR.glob("handoff_*.md"), reverse=True)
        if handoffs:
            latest_handoff = handoffs[0].name

    return {
        "total": handoff_count + doxa_count + wf_count,
        "by_type": {
            "handoff": handoff_count,
            "doxa": doxa_count,
            "workflow": wf_count,
        },
        "latest_handoff": latest_handoff,
    }
