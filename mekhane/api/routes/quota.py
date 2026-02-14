#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: /api/quota — Antigravity IDE Quota 情報エンドポイント
"""
Quota Routes — Language Server GetUserStatus API 呼び出し

GET /api/quota  — モデル別 Quota 残量と段階的ステータスを返す

戦略:
  1. agq-check.sh --json を試行
  2. 失敗時: Python で直接 LS プロセスを検出し API を呼ぶ (フォールバック)
"""

import asyncio
import json
import logging
import re
import ssl
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger("hegemonikon.api.quota")


# --- Response Models ---

class QuotaModel(BaseModel):
    """個別モデルの Quota 情報。"""
    label: str
    remaining_pct: int = Field(ge=0, le=100, description="残量パーセント")
    reset_time: str = Field(description="リセット時刻 (HH:MM UTC)")
    status: str = Field(description="green | yellow | orange | red")


class QuotaCredits(BaseModel):
    """クレジット情報。"""
    available: int
    monthly: int


class QuotaResponse(BaseModel):
    """Quota 全体レスポンス。"""
    name: str = ""
    plan: str = ""
    prompt_credits: QuotaCredits
    flow_credits: QuotaCredits
    models: list[QuotaModel] = []
    overall_status: str = Field(
        default="unknown",
        description="green | yellow | orange | red | unknown"
    )
    timestamp: str = ""
    error: str | None = None


# --- Helpers ---

_AGQ_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "agq-check.sh"

# STATUS thresholds (matching agq-check.sh L181)
def _pct_to_status(pct: int) -> str:
    if pct >= 80:
        return "green"
    elif pct >= 40:
        return "yellow"
    elif pct >= 10:
        return "orange"
    else:
        return "red"


def _parse_quota_json(raw: dict[str, Any]) -> QuotaResponse:
    """LS GetUserStatus の生 JSON を QuotaResponse に変換する。"""
    user_status = raw.get("userStatus", {})
    plan_status = user_status.get("planStatus", {})
    plan_info = plan_status.get("planInfo", {})

    name = user_status.get("name", "unknown")
    plan = user_status.get("userTier", {}).get("name", "unknown")

    pc_avail = int(plan_status.get("availablePromptCredits", 0))
    pc_monthly = int(plan_info.get("monthlyPromptCredits", 0))
    fc_avail = int(plan_status.get("availableFlowCredits", 0))
    fc_monthly = int(plan_info.get("monthlyFlowCredits", 0))

    # Parse model configs
    models: list[QuotaModel] = []
    configs = user_status.get("cascadeModelConfigData", {}).get(
        "clientModelConfigs", []
    )
    for cfg in configs:
        qi = cfg.get("quotaInfo")
        if not qi:
            continue
        label = cfg.get("label", "Unknown")
        frac = float(qi.get("remainingFraction", 0))
        pct = round(frac * 100)
        reset_raw = qi.get("resetTime", "")
        reset_time = reset_raw[11:16] if len(reset_raw) > 16 else ""
        models.append(QuotaModel(
            label=label,
            remaining_pct=pct,
            reset_time=reset_time,
            status=_pct_to_status(pct),
        ))

    # Overall status = worst model status
    status_order = {"red": 0, "orange": 1, "yellow": 2, "green": 3, "unknown": -1}
    overall = "green"
    for m in models:
        if status_order.get(m.status, -1) < status_order.get(overall, 3):
            overall = m.status

    return QuotaResponse(
        name=name,
        plan=plan,
        prompt_credits=QuotaCredits(available=pc_avail, monthly=pc_monthly),
        flow_credits=QuotaCredits(available=fc_avail, monthly=fc_monthly),
        models=models,
        overall_status=overall if models else "unknown",
        timestamp=datetime.now().isoformat(),
    )


def _empty_response(error: str) -> QuotaResponse:
    """エラー時の空レスポンスを生成する。"""
    return QuotaResponse(
        prompt_credits=QuotaCredits(available=0, monthly=0),
        flow_credits=QuotaCredits(available=0, monthly=0),
        overall_status="unknown",
        timestamp=datetime.now().isoformat(),
        error=error,
    )


# --- Direct LS API (Fallback) ---

def _discover_ls(ws_filter: str = "hegemonikon") -> tuple[str, list[int]]:
    """Language Server プロセスから CSRF トークンとポート一覧を取得する。

    Returns:
        (csrf_token, [port1, port2, ...])

    Raises:
        RuntimeError: プロセスが見つからない or CSRF が取得できない場合
    """
    # ps aux で language_server_linux を検索
    try:
        ps_result = subprocess.run(
            ["ps", "aux"],
            capture_output=True, text=True, timeout=5,
        )
    except Exception as e:
        raise RuntimeError(f"ps aux failed: {e}") from e

    proc_line = ""
    for line in ps_result.stdout.splitlines():
        if "language_server_linux" in line and ws_filter in line and "grep" not in line:
            proc_line = line
            break

    if not proc_line:
        raise RuntimeError(f"LS process not found (filter: {ws_filter})")

    # PID 抽出
    parts = proc_line.split()
    if len(parts) < 2:
        raise RuntimeError("Cannot parse PID from ps output")
    pid = parts[1]

    # CSRF トークン抽出
    csrf_match = re.search(r"csrf_token\s+(\S+)", proc_line)
    if not csrf_match:
        raise RuntimeError("CSRF token not found in process args")
    csrf = csrf_match.group(1)

    # ss でリスニングポート取得
    try:
        ss_result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True, text=True, timeout=5,
        )
    except Exception as e:
        raise RuntimeError(f"ss command failed: {e}") from e

    ports: list[int] = []
    for line in ss_result.stdout.splitlines():
        if f"pid={pid}" in line:
            port_match = re.search(r"127\.0\.0\.1:(\d+)", line)
            if port_match:
                ports.append(int(port_match.group(1)))

    if not ports:
        raise RuntimeError(f"No listening ports found for PID {pid}")

    return csrf, sorted(set(ports))


def _call_ls_api(csrf: str, ports: list[int]) -> dict[str, Any]:
    """LS の GetUserStatus API を直接呼び出す。

    Returns:
        パース済み JSON dict

    Raises:
        RuntimeError: 全ポートで失敗した場合
    """
    # Self-signed cert を無視
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    payload = json.dumps({
        "metadata": {
            "ideName": "antigravity",
            "extensionName": "antigravity",
            "locale": "en",
        }
    }).encode()

    headers = {
        "Content-Type": "application/json",
        "X-Codeium-Csrf-Token": csrf,
        "Connect-Protocol-Version": "1",
    }

    errors: list[str] = []
    for port in ports:
        url = (
            f"https://127.0.0.1:{port}"
            "/exa.language_server_pb.LanguageServerService/GetUserStatus"
        )
        req = Request(url, data=payload, headers=headers, method="POST")
        try:
            with urlopen(req, timeout=5, context=ctx) as resp:
                body = resp.read().decode()
                data = json.loads(body)
                if "userStatus" in data:
                    return data
                errors.append(f"port {port}: no userStatus in response")
        except Exception as e:
            errors.append(f"port {port}: {e}")

    raise RuntimeError(f"All ports failed: {'; '.join(errors)}")


def _fetch_quota_direct(ws_filter: str = "hegemonikon") -> QuotaResponse:
    """Python 直接呼び出しで Quota を取得する。agq-check.sh のフォールバック。"""
    csrf, ports = _discover_ls(ws_filter)
    raw = _call_ls_api(csrf, ports)
    return _parse_quota_json(raw)


# --- AGQ Script ---

def _fetch_quota_agq() -> QuotaResponse:
    """agq-check.sh --json 経由で Quota を取得する。"""
    if not _AGQ_SCRIPT.exists():
        raise FileNotFoundError(f"agq-check.sh not found: {_AGQ_SCRIPT}")

    result = subprocess.run(
        ["bash", str(_AGQ_SCRIPT), "--json"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if result.returncode != 0:
        raise RuntimeError(f"agq-check.sh exit {result.returncode}: {result.stderr[:200]}")

    raw = json.loads(result.stdout)
    return _parse_quota_json(raw)


# --- Router ---

router = APIRouter(prefix="/quota", tags=["quota"])


@router.get("", response_model=QuotaResponse)
async def get_quota() -> QuotaResponse:
    """Quota 情報を取得する。agq-check.sh → 直接 API の2段階フォールバック。"""

    # Strategy 1: agq-check.sh
    try:
        return await asyncio.to_thread(_fetch_quota_agq)
    except Exception as e:
        logger.info("agq-check.sh failed, trying direct API: %s", e)

    # Strategy 2: Direct LS API call (Python)
    try:
        return await asyncio.to_thread(_fetch_quota_direct)
    except Exception as e:
        logger.warning("Direct LS API also failed: %s", e)
        return _empty_response(str(e))
