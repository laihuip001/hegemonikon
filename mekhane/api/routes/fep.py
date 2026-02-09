# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: /api/fep/* — FEP Agent エンドポイント
"""
FEP Routes — fep_agent_v2 のラッパー

POST /api/fep/step      — 推論-行動サイクル実行
GET  /api/fep/state      — Agent 内部状態
GET  /api/fep/dashboard   — 分析データ
"""

import threading
from typing import Any, Optional

import numpy as np

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# PURPOSE: レスポンスモデル (/dia+ fix #3)
class FEPStepRequest(BaseModel):
    """FEP step リクエスト。"""
    observation: int = Field(ge=0, lt=48, description="観測インデックス (0-47)")


class FEPStepResponse(BaseModel):
    """FEP step 結果。"""
    action_name: str
    action_index: int
    selected_series: str | None = None
    explanation: str = ""
    beliefs_entropy: float | None = None


class FEPStateResponse(BaseModel):
    """Agent の内部状態。"""
    beliefs: list[float]
    epsilon: dict[str, float]
    history_length: int
    precision_weights: dict[str, float] | None = None


class FEPDashboardResponse(BaseModel):
    """ダッシュボード分析データ。"""
    total_steps: int = 0
    action_distribution: dict[str, int] = {}
    series_distribution: dict[str, int] = {}
    available: bool = True
    message: str = ""


# PURPOSE: FEP Agent シングルトン + スレッドロック (/dia+ fix #1)
_agent = None
_agent_lock = threading.RLock()  # RLock: _get_agent() + endpoint 両方で取得するため再入可能
_MAX_HISTORY = 1000  # /dia+ fix #5: history 上限ガード

router = APIRouter(prefix="/fep", tags=["fep"])


# PURPOSE: Agent の遅延初期化 (R1 fix: Double-Checked Locking)
def _get_agent():
    """FEP Agent をシングルトンで取得。スレッドセーフ。"""
    global _agent
    if _agent is None:
        with _agent_lock:
            if _agent is None:  # Double-check
                from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2
                _agent = HegemonikónFEPAgentV2(use_defaults=True)
    return _agent


@router.post("/step", response_model=FEPStepResponse)
async def fep_step(req: FEPStepRequest) -> FEPStepResponse:
    """推論-行動サイクルを1ステップ実行。"""
    with _agent_lock:  # /dia+ fix #1: race condition 防止
        agent = _get_agent()
        result = agent.step(req.observation)

        # /dia+ fix #5: history 上限ガード
        if hasattr(agent, "history") and len(agent.history) > _MAX_HISTORY:
            agent.history = agent.history[-_MAX_HISTORY:]

        explanation = ""
        try:
            explanation = agent.explain(result)
        except Exception:
            pass

        # beliefs entropy (Shannon)
        beliefs = agent._to_beliefs_array()
        eps = 1e-10
        entropy = float(-np.sum(beliefs * np.log(beliefs + eps)))

    return FEPStepResponse(
        action_name=result.get("action_name", "unknown"),
        action_index=result.get("action", -1),
        selected_series=result.get("selected_series"),
        explanation=explanation,
        beliefs_entropy=round(entropy, 4),
    )


@router.get("/state", response_model=FEPStateResponse)
async def fep_state() -> FEPStateResponse:
    """Agent の現在の内部状態を取得。"""
    with _agent_lock:
        agent = _get_agent()
        beliefs = agent._to_beliefs_array().tolist()
        epsilon = dict(agent.epsilon) if hasattr(agent, "epsilon") else {}
        history_len = len(agent.history) if hasattr(agent, "history") else 0
        precision = None
        if hasattr(agent, "precision_weights"):
            precision = {k: float(v) for k, v in agent.precision_weights.items()}

    return FEPStateResponse(
        beliefs=beliefs,
        epsilon=epsilon,
        history_length=history_len,
        precision_weights=precision,
    )


@router.get("/dashboard", response_model=FEPDashboardResponse)
async def fep_dashboard() -> FEPDashboardResponse:
    """FEP ダッシュボードデータを取得。"""
    with _agent_lock:
        agent = _get_agent()
        if not hasattr(agent, "history") or not agent.history:
            return FEPDashboardResponse(
                available=True,
                message="No history yet. Run /api/fep/step first.",
            )

        # 集計
        action_dist: dict[str, int] = {}
        series_dist: dict[str, int] = {}
        for entry in agent.history:
            action = entry.get("action_name", "unknown")
            action_dist[action] = action_dist.get(action, 0) + 1
            series = entry.get("selected_series")
            if series:
                series_dist[series] = series_dist.get(series, 0) + 1

    return FEPDashboardResponse(
        total_steps=len(agent.history),
        action_distribution=action_dist,
        series_distribution=series_dist,
    )


# =============================================================================
# Convergence Tracker — E2E endpoint
# =============================================================================

class ConvergenceRecordRequest(BaseModel):
    """Convergence 記録リクエスト。"""
    agent_series: str | None = None
    attractor_series: str | None = None
    agent_action: str = ""
    epsilon: dict[str, float] | None = None


@router.get("/convergence")
async def get_convergence():
    """現在の収束状態を取得。"""
    from mekhane.fep.convergence_tracker import convergence_summary, format_convergence
    summary = convergence_summary()
    return {
        "summary": summary,
        "formatted": format_convergence(summary),
    }


@router.post("/convergence")
async def post_convergence(req: ConvergenceRecordRequest):
    """Agent/Attractor 一致を記録。"""
    from mekhane.fep.convergence_tracker import record_agreement, format_convergence
    summary = record_agreement(
        agent_series=req.agent_series,
        attractor_series=req.attractor_series,
        agent_action=req.agent_action,
        epsilon=req.epsilon,
    )
    return {
        "summary": summary,
        "formatted": format_convergence(summary),
    }
