# PROOF: [L2/インフラ] <- mekhane/basanos/gateway/ A0→MCP統合が必要→VirtualServerが担う
# PURPOSE: Virtual MCP Server — 複数の下流 MCP サーバーを束ねて単一サーバーとして公開
"""
Virtual MCP Server — 複数の下流 MCP サーバーを束ねて単一サーバーとして公開

名前空間管理、ツールルーティング、Policy チェック、エラー統一処理を提供する。
"""

from __future__ import annotations

import json
import logging
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any

from mekhane.basanos.gateway.auth_proxy import AuthProxy
from mekhane.basanos.gateway.discovery import DiscoveryEngine, ServerInfo, TransportType
from mekhane.basanos.gateway.policy_enforcer import PolicyDecision, PolicyEnforcer, PolicyResult

logger = logging.getLogger(__name__)


# PURPOSE: の統一的インターフェースを実現する
@dataclass
class ToolRoute:
    """ツールのルーティング情報"""
    server_name: str
    tool_name: str
    namespaced_name: str
    description: str = ""


# PURPOSE: の統一的インターフェースを実現する
@dataclass
class GatewayError:
    """Gateway エラーの統一フォーマット"""
    code: str
    message: str
    server_name: str = ""
    tool_name: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    # PURPOSE: virtual_server の to dict 処理を実行する
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


# PURPOSE: の統一的インターフェースを実現する
@dataclass
class RouteResult:
    """ルーティング結果"""
    success: bool
    server_info: ServerInfo | None = None
    tool_name: str = ""
    policy_result: PolicyResult | None = None
    error: GatewayError | None = None
    auth_headers: dict[str, str] = field(default_factory=dict)


# PURPOSE: 下流サーバーへの転送結果を格納する
@dataclass
class ForwardResult:
    """forward() の結果"""
    success: bool
    response: dict[str, Any] = field(default_factory=dict)
    error: GatewayError | None = None
    latency_ms: float = 0.0
    transport_used: str = ""


# PURPOSE: の統一的インターフェースを実現する
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

    # PURPOSE: tool を登録する
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

    # PURPOSE: server tools を登録する
    def register_server_tools(self, server_name: str, tools: list[str]) -> int:
        """サーバーの全ツールを一括登録"""
        for tool in tools:
            self.register_tool(server_name, tool)
        return len(tools)

    # PURPOSE: virtual_server の route 処理を実行する
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

    # PURPOSE: route() の結果を使って下流サーバーにリクエストを転送する
    def forward(
        self,
        namespaced_tool: str,
        arguments: dict[str, Any] | None = None,
        timeout_seconds: float = 30.0,
    ) -> ForwardResult:
        """
        route() → 転送の一体化パイプライン。

        名前空間付きツール名を解決し、下流 MCP サーバーに
        JSON-RPC メッセージを送信して応答を返す。

        Args:
            namespaced_tool: "server_name.tool_name" 形式
            arguments: ツールに渡す引数
            timeout_seconds: タイムアウト (秒)

        Returns:
            ForwardResult: 転送結果

        Notes:
            - stdio: subprocess で起動し JSON-RPC を stdin/stdout で通信
            - streamable-http/sse: httpx で POST リクエスト送信
        """
        start_time = time.monotonic()
        arguments = arguments or {}

        # Step 1: ルーティング解決
        route_result = self.route(namespaced_tool)
        if not route_result.success:
            elapsed = (time.monotonic() - start_time) * 1000
            return ForwardResult(
                success=False,
                error=route_result.error,
                latency_ms=elapsed,
            )

        server_info = route_result.server_info
        tool_name = route_result.tool_name
        assert server_info is not None  # route() guarantees this on success

        # Step 2: MCP JSON-RPC メッセージの構築
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        # Step 3: トランスポートに応じた転送
        try:
            if server_info.transport == TransportType.STDIO:
                result = self._forward_stdio(
                    server_info, jsonrpc_request, timeout_seconds
                )
            elif server_info.transport in (
                TransportType.STREAMABLE_HTTP,
                TransportType.SSE,
            ):
                result = self._forward_http(
                    server_info, jsonrpc_request, route_result.auth_headers, timeout_seconds
                )
            else:
                elapsed = (time.monotonic() - start_time) * 1000
                return ForwardResult(
                    success=False,
                    error=GatewayError(
                        code="UNSUPPORTED_TRANSPORT",
                        message=f"Transport '{server_info.transport}' is not supported",
                        server_name=server_info.name,
                        tool_name=tool_name,
                    ),
                    latency_ms=elapsed,
                )

            result.latency_ms = (time.monotonic() - start_time) * 1000
            return result

        except Exception as e:
            elapsed = (time.monotonic() - start_time) * 1000
            logger.error("Forward failed: %s", e, exc_info=True)
            return ForwardResult(
                success=False,
                error=GatewayError(
                    code="FORWARD_ERROR",
                    message=str(e),
                    server_name=server_info.name,
                    tool_name=tool_name,
                ),
                latency_ms=elapsed,
            )

    def _forward_stdio(
        self,
        server_info: ServerInfo,
        request: dict[str, Any],
        timeout: float,
    ) -> ForwardResult:
        """stdio トランスポートで下流サーバーにリクエストを転送する。

        MCP JSON-RPC プロトコルに従い、subprocess の
        stdin/stdout 経由で通信する。
        """
        if not server_info.command:
            return ForwardResult(
                success=False,
                error=GatewayError(
                    code="NO_COMMAND",
                    message=f"No command configured for stdio server '{server_info.name}'",
                    server_name=server_info.name,
                ),
                transport_used="stdio",
            )

        # JSON-RPC メッセージを送信
        request_json = json.dumps(request)
        cmd = shlex.split(server_info.command)

        try:
            proc = subprocess.run(
                cmd,
                input=request_json,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return ForwardResult(
                success=False,
                error=GatewayError(
                    code="TIMEOUT",
                    message=f"stdio server '{server_info.name}' timed out after {timeout}s",
                    server_name=server_info.name,
                ),
                transport_used="stdio",
            )
        except FileNotFoundError:
            return ForwardResult(
                success=False,
                error=GatewayError(
                    code="COMMAND_NOT_FOUND",
                    message=f"Command not found: {cmd[0]}",
                    server_name=server_info.name,
                ),
                transport_used="stdio",
            )

        if proc.returncode != 0:
            return ForwardResult(
                success=False,
                error=GatewayError(
                    code="PROCESS_ERROR",
                    message=f"Server exited with code {proc.returncode}: {proc.stderr[:200]}",
                    server_name=server_info.name,
                ),
                transport_used="stdio",
            )

        # JSON-RPC レスポンスをパース
        try:
            response = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return ForwardResult(
                success=False,
                error=GatewayError(
                    code="INVALID_RESPONSE",
                    message=f"Invalid JSON from server: {proc.stdout[:200]}",
                    server_name=server_info.name,
                ),
                transport_used="stdio",
            )

        # JSON-RPC error チェック
        if "error" in response:
            return ForwardResult(
                success=False,
                response=response,
                error=GatewayError(
                    code="JSONRPC_ERROR",
                    message=response["error"].get("message", "Unknown error"),
                    server_name=server_info.name,
                    details=response["error"],
                ),
                transport_used="stdio",
            )

        return ForwardResult(
            success=True,
            response=response,
            transport_used="stdio",
        )

    def _forward_http(
        self,
        server_info: ServerInfo,
        request: dict[str, Any],
        auth_headers: dict[str, str],
        timeout: float,
    ) -> ForwardResult:
        """HTTP トランスポートで下流サーバーにリクエストを転送する。

        Streamable HTTP / SSE 両方に対応。
        httpx がインストールされていない場合は ImportError を返す。
        """
        if not server_info.url:
            return ForwardResult(
                success=False,
                error=GatewayError(
                    code="NO_URL",
                    message=f"No URL configured for HTTP server '{server_info.name}'",
                    server_name=server_info.name,
                ),
                transport_used="http",
            )

        try:
            import httpx  # noqa: AI-019 optional dependency
        except ImportError:
            return ForwardResult(
                success=False,
                error=GatewayError(
                    code="MISSING_DEPENDENCY",
                    message="httpx is required for HTTP transport: pip install httpx",
                    server_name=server_info.name,
                ),
                transport_used="http",
            )

        headers = {
            "Content-Type": "application/json",
            **auth_headers,
        }

        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(
                    server_info.url,
                    json=request,
                    headers=headers,
                )
                resp.raise_for_status()
                response = resp.json()
        except httpx.TimeoutException:
            return ForwardResult(
                success=False,
                error=GatewayError(
                    code="TIMEOUT",
                    message=f"HTTP server '{server_info.name}' timed out after {timeout}s",
                    server_name=server_info.name,
                ),
                transport_used="http",
            )
        except httpx.HTTPStatusError as e:
            return ForwardResult(
                success=False,
                error=GatewayError(
                    code="HTTP_ERROR",
                    message=f"HTTP {e.response.status_code}: {e.response.text[:200]}",
                    server_name=server_info.name,
                ),
                transport_used="http",
            )
        except Exception as e:
            return ForwardResult(
                success=False,
                error=GatewayError(
                    code="HTTP_ERROR",
                    message=str(e),
                    server_name=server_info.name,
                ),
                transport_used="http",
            )

        # JSON-RPC error チェック
        if "error" in response:
            return ForwardResult(
                success=False,
                response=response,
                error=GatewayError(
                    code="JSONRPC_ERROR",
                    message=response["error"].get("message", "Unknown error"),
                    server_name=server_info.name,
                    details=response["error"],
                ),
                transport_used="http",
            )

        return ForwardResult(
            success=True,
            response=response,
            transport_used="http",
        )

    # PURPOSE: virtual_server の list tools 処理を実行する
    def list_tools(self) -> list[ToolRoute]:
        """登録済みツールの一覧"""
        return list(self._tools.values())

    # PURPOSE: virtual_server の list tools by server 処理を実行する
    def list_tools_by_server(self, server_name: str) -> list[ToolRoute]:
        """特定サーバーのツール一覧"""
        return [t for t in self._tools.values() if t.server_name == server_name]

    # PURPOSE: virtual_server の tool count 処理を実行する
    @property
    def tool_count(self) -> int:
        return len(self._tools)

    # PURPOSE: status を取得する
    def get_status(self) -> dict[str, Any]:
        """Gateway 全体のステータス"""
        return {
            "servers_registered": self._discovery.server_count,
            "tools_registered": self.tool_count,
            "policies_loaded": self._policy.policy_count,
            "auth_configs": self._auth.config_count,
            "servers": list(self._discovery.servers.keys()),
        }
