#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: MCP Gateway のステータスと管理 API
"""
Gateway Router — MCP Gateway の REST API エンドポイント

エンドポイント:
  GET  /gateway/status   — Gateway 全体のステータス
  GET  /gateway/servers   — 登録済みサーバー一覧
  GET  /gateway/policies  — ロード済みポリシー一覧
  POST /gateway/check     — ツール呼び出しの事前チェック
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["gateway"])

# --- Lazy singleton ---

_gateway = None


def _get_gateway():
    """Gateway コンポーネントを遅延初期化する"""
    global _gateway
    if _gateway is not None:
        return _gateway

    from mekhane.synedrion.gateway.discovery import DiscoveryEngine
    from mekhane.synedrion.gateway.policy_enforcer import PolicyEnforcer
    from mekhane.synedrion.gateway.auth_proxy import AuthProxy
    from mekhane.synedrion.gateway.virtual_server import VirtualServer

    discovery = DiscoveryEngine()
    discovery.register_local_defaults()
    enforcer = PolicyEnforcer()
    auth = AuthProxy()
    vs = VirtualServer(discovery, enforcer, auth)

    # 標準ツール登録
    standard_tools = {
        "gnosis": ["search", "stats", "recommend_model"],
        "sophia": ["search", "stats", "backlinks", "graph_stats"],
        "hermeneus": [
            "hermeneus_dispatch", "hermeneus_execute",
            "hermeneus_compile", "hermeneus_audit",
            "hermeneus_list_workflows", "hermeneus_export_session",
        ],
        "sympatheia": [
            "sympatheia_status", "sympatheia_wbc",
            "sympatheia_notifications", "sympatheia_feedback",
            "sympatheia_digest", "sympatheia_attractor",
        ],
        "mneme": ["search", "sources", "stats"],
        "digestor": ["get_topics", "list_candidates", "run_digestor"],
        "jules": ["jules_create_task", "jules_get_status", "jules_list_repos", "jules_batch_execute"],
        "prompt-lang": ["generate"],
        "sequential-thinking": ["sequentialthinking"],
    }
    for server, tools in standard_tools.items():
        vs.register_server_tools(server, tools)

    _gateway = {
        "discovery": discovery,
        "enforcer": enforcer,
        "auth": auth,
        "virtual_server": vs,
    }
    logger.info("Gateway initialized: %d servers, %d tools",
                discovery.server_count, vs.tool_count)
    return _gateway


# --- Models ---

class CheckRequest(BaseModel):
    """ツール呼び出しの事前チェック"""
    server_name: str
    tool_name: str


class CheckResponse(BaseModel):
    """チェック結果"""
    allowed: bool
    decision: str
    reason: str
    policy_name: str = ""
    message: str = ""


# --- Endpoints ---

@router.get("/gateway/status")
async def gateway_status() -> dict[str, Any]:
    """Gateway 全体のステータスを返す"""
    gw = _get_gateway()
    vs = gw["virtual_server"]
    return {
        "status": "operational",
        "gateway": vs.get_status(),
    }


@router.get("/gateway/servers")
async def gateway_servers() -> dict[str, Any]:
    """登録済みサーバーの一覧"""
    gw = _get_gateway()
    discovery = gw["discovery"]
    servers = {}
    for name, info in discovery.servers.items():
        servers[name] = {
            "transport": info.transport.value,
            "is_local": info.is_local,
            "command": info.command,
            "url": info.url,
            "tools_count": len(info.tools),
        }
    return {"servers": servers, "total": len(servers)}


@router.get("/gateway/policies")
async def gateway_policies() -> dict[str, Any]:
    """ロード済みポリシーの一覧"""
    gw = _get_gateway()
    enforcer = gw["enforcer"]
    return {
        "policy_count": enforcer.policy_count,
        "allowed_servers": sorted(enforcer.get_server_list()),
    }


@router.post("/gateway/check")
async def gateway_check(req: CheckRequest) -> CheckResponse:
    """ツール呼び出しの事前ポリシーチェック"""
    gw = _get_gateway()
    enforcer = gw["enforcer"]
    result = enforcer.check(req.server_name, req.tool_name)
    return CheckResponse(
        allowed=result.decision.value == "allow",
        decision=result.decision.value,
        reason=result.reason,
        policy_name=result.policy_name,
        message=result.message,
    )
