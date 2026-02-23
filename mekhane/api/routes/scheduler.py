#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: Jules Scheduler ダッシュボードカード用 API
"""
Scheduler Status API

直近の scheduler ログを読み取り、ダッシュボード用のサマリーを返す。
"""

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter

logger = logging.getLogger("hegemonikon.api.scheduler")

router = APIRouter(tags=["scheduler"])

# PURPOSE: ログディレクトリ
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = _PROJECT_ROOT / "logs" / "specialist_daily"


# PURPOSE: 直近 N 件の scheduler ログからサマリーを生成する。
@router.get("/scheduler/status")
async def scheduler_status(limit: int = 5) -> dict:
    """直近 N 件の scheduler ログからサマリーを生成する。"""
    if not LOG_DIR.exists():
        return {
            "status": "no_data",
            "message": "ログディレクトリ未検出",
            "runs": [],
            "summary": None,
        }

    # scheduler_YYYYMMDD_HHMM.json を日付降順で取得
    log_files = sorted(LOG_DIR.glob("scheduler_*.json"), reverse=True)

    if not log_files:
        return {
            "status": "no_data",
            "message": "実行ログなし",
            "runs": [],
            "summary": None,
        }

    runs: list[dict] = []
    total_files = 0
    total_started = 0
    total_failed = 0
    modes_seen: dict[str, int] = {}

    for log_file in log_files[:limit]:
        try:
            data = json.loads(log_file.read_text())
            # NEW-1b: 旧ログ (result 内ネスト) / 新ログ (トップレベル) 両対応
            result = data.get("result", {})
            run = {
                "filename": log_file.name,
                "timestamp": data.get("timestamp", ""),
                "slot": data.get("slot", ""),
                "mode": data.get("mode", "specialist"),
                "total_tasks": data.get("total_tasks") or result.get("total_tasks", 0),
                "total_started": data.get("total_started") or result.get("total_started", 0),
                "total_failed": data.get("total_failed") or result.get("total_failed", 0),
                "files_reviewed": data.get("files_reviewed") or len(result.get("files", [])),
                "dynamic": data.get("dynamic", False),
            }
            runs.append(run)
            total_files += run["files_reviewed"]
            total_started += run["total_started"]
            total_failed += run["total_failed"]

            mode = run["mode"]
            modes_seen[mode] = modes_seen.get(mode, 0) + 1
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Failed to parse %s: %s", log_file.name, exc)

    # 成功率を計算
    success_rate = (
        round((total_started - total_failed) / total_started * 100, 1)
        if total_started > 0
        else 0.0
    )

    # ステータス判定
    if success_rate >= 90:
        status = "ok"
    elif success_rate >= 70:
        status = "warn"
    else:
        status = "error"

    summary = {
        "total_runs": len(runs),
        "total_files_reviewed": total_files,
        "total_started": total_started,
        "total_failed": total_failed,
        "success_rate": success_rate,
        "modes": modes_seen,
        "status": status,
    }

    return {
        "status": status,
        "runs": runs,
        "summary": summary,
    }


# PURPOSE: 直近 N 日間の日別成功率推移 (スパークライン用)。
@router.get("/scheduler/trend")
async def scheduler_trend(days: int = 14) -> dict:
    """直近 N 日間の日別成功率推移 (スパークライン用)。"""
    if not LOG_DIR.exists():
        return {"trend": [], "days": days}

    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=days)

    # 全ログを日付ごとに集計
    daily: dict[str, dict] = {}
    for log_file in sorted(LOG_DIR.glob("scheduler_*.json")):
        try:
            data = json.loads(log_file.read_text())
            ts = data.get("timestamp", "")
            if not ts:
                continue
            date_str = ts[:10]  # "YYYY-MM-DD"
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if dt < cutoff:
                continue

            result = data.get("result", {})
            started = data.get("total_started") or result.get("total_started", 0)
            failed = data.get("total_failed") or result.get("total_failed", 0)

            if date_str not in daily:
                daily[date_str] = {"started": 0, "failed": 0, "runs": 0}
            daily[date_str]["started"] += started
            daily[date_str]["failed"] += failed
            daily[date_str]["runs"] += 1
        except (json.JSONDecodeError, KeyError, ValueError):
            continue

    trend = []
    for date_str in sorted(daily.keys()):
        d = daily[date_str]
        rate = round((d["started"] - d["failed"]) / d["started"] * 100, 1) if d["started"] > 0 else 0.0
        trend.append({
            "date": date_str,
            "success_rate": rate,
            "runs": d["runs"],
            "started": d["started"],
            "failed": d["failed"],
        })

    return {"trend": trend, "days": days}


# PURPOSE: Specialist 効果分析データ (Perspective ランキング + domain/axis 集計)。
@router.get("/scheduler/analysis")
async def scheduler_analysis() -> dict:
    """Specialist 効果分析データ (Perspective ランキング + domain/axis 集計)。"""
    try:
        from mekhane.symploke.specialist_analyzer import full_analysis
        from mekhane.symploke.basanos_feedback import FeedbackStore
        store = FeedbackStore()
        return full_analysis(store, top=20)
    except Exception as exc:
        logger.warning("Analysis failed: %s", exc)
        return {"ranking": [], "by_domain": [], "by_axis": [], "error": str(exc)}


# PURPOSE: F17: Perspective 進化提案 (perspective_evolver)。
@router.get("/scheduler/evolution")
async def scheduler_evolution() -> dict:
    """F17: Perspective 進化提案 (perspective_evolver)。"""
    try:
        from mekhane.symploke.perspective_evolver import evolve
        from mekhane.symploke.basanos_feedback import FeedbackStore
        store = FeedbackStore()
        return evolve(store, dry_run=True)
    except Exception as exc:
        logger.warning("Evolution failed: %s", exc)
        return {"proposals": [], "applied": 0, "dry_run": True, "error": str(exc)}


# PURPOSE: F18: 適応ローテーション現況 (adaptive_rotation)。
@router.get("/scheduler/rotation")
async def scheduler_rotation() -> dict:
    """F18: 適応ローテーション現況 (adaptive_rotation)。"""
    try:
        from mekhane.symploke.adaptive_rotation import get_rotation_report
        return get_rotation_report()
    except Exception as exc:
        logger.warning("Rotation report failed: %s", exc)
        return {"mode_scores": {}, "rotation": {}, "error": str(exc)}
