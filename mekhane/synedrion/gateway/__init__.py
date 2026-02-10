"""
synedrion.gateway — MCP Gateway

外部 MCP サーバー群へのアクセスを一元管理する Gateway。
4コンポーネント: PolicyEnforcer, DiscoveryEngine, AuthProxy, VirtualServer
"""

from mekhane.synedrion.gateway.policy_enforcer import PolicyEnforcer, PolicyDecision
from mekhane.synedrion.gateway.discovery import DiscoveryEngine, ServerInfo
from mekhane.synedrion.gateway.auth_proxy import AuthProxy
from mekhane.synedrion.gateway.virtual_server import VirtualServer

__all__ = [
    "PolicyEnforcer",
    "PolicyDecision",
    "DiscoveryEngine",
    "ServerInfo",
    "AuthProxy",
    "VirtualServer",
]
