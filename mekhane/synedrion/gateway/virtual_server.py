"""
Virtual MCP Server — 複数の下流 MCP サーバーを束ねて単一サーバーとして公開

名前空間管理、ツールルーティング、Policy チェック、エラー統一処理を提供する。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from mekhane.synedrion.gateway.auth_proxy import AuthProxy
from mekhane.synedrion.gateway.discovery import DiscoveryEngine, ServerInfo
from mekhane.synedrion.gateway.policy_enforcer import PolicyDecision, PolicyEnforcer, PolicyResult

logger = logging.getLogger(__name__)


@dataclass
class ToolRoute:
    """ツールのルーティング情報"""
    server_name: str
    tool_name: str
    namespaced_name: str
    description: str = ""


@dataclass
class GatewayError:
    """Gateway エラーの統一フォーマット"""
    code: str
    message: str
    server_name: str = ""
    tool_name: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "server": self.server_name,
                "tool": self.tool_name,
                **self.details,
            }
        }


@dataclass
class RouteResult:
    """ルーティング結果"""
    success: bool
    server_info: ServerInfo | None = None
    tool_name: str = ""
    policy_result: PolicyResult | None = None
    error: GatewayError | None = None
    auth_headers: dict[str, str] = field(default_factory=dict)


class VirtualServer:
    """
    複数の MCP サーバーを束ねる仮想サーバー。

    名前空間 (server_name.tool_name) でツールを管理し、
    呼び出し時に Policy チェック → Auth → ルーティングを実行する。

    使用例:
        # コンポーネント初期化
        discovery = DiscoveryEngine()
        discovery.register_local_defaults()

        enforcer = PolicyEnforcer()
        auth = AuthProxy()

        # Virtual Server 構成
        vs = VirtualServer(discovery, enforcer, auth)

        # ツール登録
        vs.register_tool("gnosis", "search", "Gnōsis知識ベースを検索")
        vs.register_tool("sophia", "search", "Sophia KIを検索")

        # ルーティング
        result = vs.route("gnosis.search")
        if result.success:
            # result.server_info, result.tool_name で下流サーバーに転送
            pass
    """

    def __init__(
        self,
        discovery: DiscoveryEngine,
        policy: PolicyEnforcer,
        auth: AuthProxy,
    ) -> None:
        self._discovery = discovery
        self._policy = policy
        self._auth = auth
        self._tools: dict[str, ToolRoute] = {}

    def register_tool(
        self,
        server_name: str,
        tool_name: str,
        description: str = "",
    ) -> str:
        """
        ツールを名前空間付きで登録する。

        Args:
            server_name: MCP サーバー名
            tool_name: ツール名
            description: ツールの説明

        Returns:
            名前空間付きツール名 (例: "gnosis.search")
        """
        namespaced = f"{server_name}.{tool_name}"
        self._tools[namespaced] = ToolRoute(
            server_name=server_name,
            tool_name=tool_name,
            namespaced_name=namespaced,
            description=description,
        )
        logger.debug("Registered tool: %s", namespaced)
        return namespaced

    def register_server_tools(self, server_name: str, tools: list[str]) -> int:
        """サーバーの全ツールを一括登録"""
        for tool in tools:
            self.register_tool(server_name, tool)
        return len(tools)

    def route(self, namespaced_tool: str) -> RouteResult:
        """
        名前空間付きツール名からルーティングを解決する。

        Args:
            namespaced_tool: "server_name.tool_name" 形式

        Returns:
            RouteResult: ルーティング結果 (成功/失敗 + 詳細情報)
        """
        # 1. 名前空間の分割
        parts = namespaced_tool.split(".", 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return RouteResult(
                success=False,
                error=GatewayError(
                    code="INVALID_NAMESPACE",
                    message=f"Invalid tool name format: '{namespaced_tool}'. "
                            f"Expected 'server_name.tool_name'.",
                    tool_name=namespaced_tool,
                ),
            )

        server_name, tool_name = parts

        # 2. サーバーの存在確認
        server_info = self._discovery.get(server_name)
        if server_info is None:
            return RouteResult(
                success=False,
                error=GatewayError(
                    code="SERVER_NOT_FOUND",
                    message=f"Server '{server_name}' is not registered",
                    server_name=server_name,
                    tool_name=tool_name,
                ),
            )

        # 3. Policy チェック
        policy_result = self._policy.check(server_name, tool_name)
        if policy_result.decision == PolicyDecision.DENY:
            return RouteResult(
                success=False,
                policy_result=policy_result,
                error=GatewayError(
                    code="POLICY_DENIED",
                    message=policy_result.reason,
                    server_name=server_name,
                    tool_name=tool_name,
                    details={"policy": policy_result.policy_name},
                ),
            )

        if policy_result.decision == PolicyDecision.REQUIRE_APPROVAL:
            return RouteResult(
                success=False,
                server_info=server_info,
                tool_name=tool_name,
                policy_result=policy_result,
                error=GatewayError(
                    code="APPROVAL_REQUIRED",
                    message=policy_result.message or policy_result.reason,
                    server_name=server_name,
                    tool_name=tool_name,
                    details={"policy": policy_result.policy_name},
                ),
            )

        # 4. 認証
        auth_ctx = self._auth.authenticate(server_name)
        if not auth_ctx.authenticated:
            return RouteResult(
                success=False,
                error=GatewayError(
                    code="AUTH_FAILED",
                    message=f"Authentication failed for server '{server_name}'",
                    server_name=server_name,
                    tool_name=tool_name,
                ),
            )

        # 5. 成功
        return RouteResult(
            success=True,
            server_info=server_info,
            tool_name=tool_name,
            policy_result=policy_result,
            auth_headers=auth_ctx.headers,
        )

    def list_tools(self) -> list[ToolRoute]:
        """登録済みツールの一覧"""
        return list(self._tools.values())

    def list_tools_by_server(self, server_name: str) -> list[ToolRoute]:
        """特定サーバーのツール一覧"""
        return [t for t in self._tools.values() if t.server_name == server_name]

    @property
    def tool_count(self) -> int:
        return len(self._tools)

    def get_status(self) -> dict[str, Any]:
        """Gateway 全体のステータス"""
        return {
            "servers_registered": self._discovery.server_count,
            "tools_registered": self.tool_count,
            "policies_loaded": self._policy.policy_count,
            "auth_configs": self._auth.config_count,
            "servers": list(self._discovery.servers.keys()),
        }
