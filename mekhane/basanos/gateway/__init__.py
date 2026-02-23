# PROOF: [L2/インフラ] <- mekhane/basanos/gateway/ A0→MCP Gateway統合が必要→gatewayパッケージが担う
# PURPOSE: basanos.gateway — MCP Gateway
"""
basanos.gateway — MCP Gateway

外部 MCP サーバー群へのアクセスを一元管理する Gateway。
4コンポーネント: PolicyEnforcer, DiscoveryEngine, AuthProxy, VirtualServer
"""

from mekhane.basanos.gateway.policy_enforcer import PolicyEnforcer, PolicyDecision
from mekhane.basanos.gateway.discovery import DiscoveryEngine, ServerInfo
from mekhane.basanos.gateway.auth_proxy import AuthProxy
from mekhane.basanos.gateway.virtual_server import VirtualServer

__all__ = [
    "PolicyEnforcer",
    "PolicyDecision",
    "DiscoveryEngine",
    "ServerInfo",
    "AuthProxy",
    "VirtualServer",
]
