# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: /api/aristos/* — Aristos L2 Evolution ダッシュボード
"""
Aristos Routes — GA 進化結果の閲覧

GET  /api/aristos/weights    — 全定理の進化済み重みを取得
GET  /api/aristos/status     — 進化状況サマリー
"""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

# PURPOSE: 重みファイルパス
EVOLVED_WEIGHTS = Path("/home/makaron8426/oikos/mneme/.hegemonikon/evolved_weights.json")
FEEDBACK_JSON = Path("/home/makaron8426/oikos/mneme/.hegemonikon/feedback.json")

router = APIRouter(prefix="/aristos", tags=["aristos"])


# PURPOSE: 重みレスポンスモデル
class WeightsResponse(BaseModel):
    """進化済み重み一覧。"""
    weights: dict[str, float] = {}
    fitness_by_theorem: dict[str, dict[str, Any]] = {}
    total_keys: int = 0
    total_theorems: int = 0


# PURPOSE: ステータスレスポンスモデル
class StatusResponse(BaseModel):
    """Aristos 進化ステータス。"""
    has_weights: bool = False
    has_feedback: bool = False
    total_weights: int = 0
    total_theorems: int = 0
    total_feedback: int = 0
    theorems: list[dict[str, Any]] = []


# PURPOSE: 全定理の進化済み重みを取得。
@router.get("/weights", response_model=WeightsResponse)
async def get_weights() -> WeightsResponse:
    """全定理の進化済み重みを取得。"""
    if not EVOLVED_WEIGHTS.exists():
        return WeightsResponse()

    try:
        data = json.loads(EVOLVED_WEIGHTS.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return WeightsResponse()

    weights = data.get("weights", {})
    fitness = data.get("fitness_by_theorem", {})

    return WeightsResponse(
        weights=weights,
        fitness_by_theorem=fitness,
        total_keys=len(weights),
        total_theorems=len(fitness),
    )


# PURPOSE: Aristos 進化ステータスを取得。
@router.get("/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """Aristos 進化ステータスを取得。"""
    has_weights = EVOLVED_WEIGHTS.exists()
    has_feedback = FEEDBACK_JSON.exists()

    total_weights = 0
    total_theorems = 0
    theorems_list: list[dict[str, Any]] = []

    if has_weights:
        try:
            data = json.loads(EVOLVED_WEIGHTS.read_text(encoding="utf-8"))
            weights = data.get("weights", {})
            fitness = data.get("fitness_by_theorem", {})
            total_weights = len(weights)
            total_theorems = len(fitness)

            for th, info in sorted(fitness.items()):
                # 該当定理の重みを抽出
                th_weights = {
                    k.split(":")[1]: round(v, 4)
                    for k, v in weights.items()
                    if k.startswith(f"{th}:")
                }
                theorems_list.append({
                    "theorem": th,
                    "scalar": round(info.get("scalar", 0.0), 3),
                    "generation": info.get("generation", 0),
                    "weights": th_weights,
                    "depth": round(info.get("depth", 0.0), 3),
                    "precision": round(info.get("precision", 0.0), 3),
                    "efficiency": round(info.get("efficiency", 0.0), 3),
                    "novelty": round(info.get("novelty", 0.0), 3),
                })
        except (json.JSONDecodeError, OSError):
            pass

    total_feedback = 0
    if has_feedback:
        try:
            fd = json.loads(FEEDBACK_JSON.read_text(encoding="utf-8"))
            if isinstance(fd, dict):
                total_feedback = len(fd.get("feedback", []))
            elif isinstance(fd, list):
                total_feedback = len(fd)
        except (json.JSONDecodeError, OSError):
            pass

    return StatusResponse(
        has_weights=has_weights,
        has_feedback=has_feedback,
        total_weights=total_weights,
        total_theorems=total_theorems,
        total_feedback=total_feedback,
        theorems=theorems_list,
    )
