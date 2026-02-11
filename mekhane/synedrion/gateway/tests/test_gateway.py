"""
MCP Gateway — 統合テスト

4コンポーネント (PolicyEnforcer, DiscoveryEngine, AuthProxy, VirtualServer) の
ユニットテストを網羅する。
"""

from __future__ import annotations

import pytest

from mekhane.synedrion.gateway.auth_proxy import AuthContext, AuthMode, AuthProxy, ServerAuthConfig
from mekhane.synedrion.gateway.discovery import DiscoveryEngine, ServerInfo, TransportType
from mekhane.synedrion.gateway.policy_enforcer import PolicyDecision, PolicyEnforcer
from mekhane.synedrion.gateway.virtual_server import VirtualServer


# =============================================================================
# PolicyEnforcer テスト
# =============================================================================

class TestPolicyEnforcer:
    """Policy Enforcer のテスト"""

    def test_load_default_policy(self) -> None:
        """デフォルト policy.yaml が正しくロードされる"""
        enforcer = PolicyEnforcer()
        assert enforcer.policy_count > 0

    def test_allowed_server(self) -> None:
        """許可リストのサーバーは ALLOW"""
        enforcer = PolicyEnforcer()
        result = enforcer.check("gnosis", "search")
        assert result.decision == PolicyDecision.ALLOW

    def test_denied_server(self) -> None:
        """未登録サーバーは DENY"""
        enforcer = PolicyEnforcer()
        result = enforcer.check("malicious_server", "steal_data")
        assert result.decision == PolicyDecision.DENY

    def test_destructive_operation_requires_approval(self) -> None:
        """破壊的操作は REQUIRE_APPROVAL"""
        enforcer = PolicyEnforcer()
        result = enforcer.check("gnosis", "delete_paper")
        assert result.decision == PolicyDecision.REQUIRE_APPROVAL

    def test_destructive_wildcard_suffix(self) -> None:
        """*_destroy パターンがマッチする"""
        enforcer = PolicyEnforcer()
        result = enforcer.check("sophia", "index_destroy")
        assert result.decision == PolicyDecision.REQUIRE_APPROVAL

    def test_normal_tool_allowed(self) -> None:
        """通常のツール呼び出しは ALLOW"""
        enforcer = PolicyEnforcer()
        result = enforcer.check("hermeneus", "dispatch")
        assert result.decision == PolicyDecision.ALLOW

    def test_rate_limit_enforcement(self) -> None:
        """レートリミットが発動する"""
        enforcer = PolicyEnforcer()
        # 60回呼んで枯渇させる
        for _ in range(60):
            enforcer.check("gnosis", "search")
        # 61回目は DENY
        result = enforcer.check("gnosis", "search")
        assert result.decision == PolicyDecision.DENY
        assert "Rate limit" in result.reason

    def test_get_server_list(self) -> None:
        """許可サーバーリストが取得できる"""
        enforcer = PolicyEnforcer()
        servers = enforcer.get_server_list()
        assert "gnosis" in servers
        assert "sophia" in servers
        assert "hermeneus" in servers


# =============================================================================
# DiscoveryEngine テスト
# =============================================================================

class TestDiscoveryEngine:
    """Discovery Engine のテスト"""

    def test_register_server(self) -> None:
        """サーバーを手動登録できる"""
        engine = DiscoveryEngine()
        engine.register(ServerInfo(
            name="test_server",
            transport=TransportType.STDIO,
            command="python test.py",
        ))
        assert engine.server_count == 1
        assert engine.get("test_server") is not None

    def test_unregister_server(self) -> None:
        """サーバー登録を解除できる"""
        engine = DiscoveryEngine()
        engine.register(ServerInfo(name="temp", transport=TransportType.STDIO))
        assert engine.unregister("temp") is True
        assert engine.server_count == 0
        assert engine.unregister("nonexistent") is False

    def test_register_local_defaults(self) -> None:
        """HGK 標準サーバーが全て登録される"""
        engine = DiscoveryEngine()
        count = engine.register_local_defaults()
        assert count == 9
        assert engine.get("gnosis") is not None
        assert engine.get("sophia") is not None

    def test_server_info_properties(self) -> None:
        """ServerInfo のプロパティが正しい"""
        local = ServerInfo(name="local", transport=TransportType.STDIO, command="python x.py")
        assert local.is_local is True
        assert local.is_remote is False

        remote = ServerInfo(name="remote", transport=TransportType.STREAMABLE_HTTP, url="https://example.com")
        assert remote.is_local is False
        assert remote.is_remote is True


# =============================================================================
# AuthProxy テスト
# =============================================================================

class TestAuthProxy:
    """Auth Proxy のテスト"""

    def test_passthrough_default(self) -> None:
        """未設定サーバーはパススルー"""
        proxy = AuthProxy()
        ctx = proxy.authenticate("gnosis")
        assert ctx.is_passthrough is True
        assert ctx.authenticated is True
        assert len(ctx.headers) == 0

    def test_api_key_auth(self) -> None:
        """API キー認証が設定される"""
        proxy = AuthProxy()
        proxy.configure_server(ServerAuthConfig(
            server_name="external",
            mode=AuthMode.API_KEY,
            api_key="test-key-123",
        ))
        ctx = proxy.authenticate("external")
        assert ctx.mode == AuthMode.API_KEY
        assert ctx.authenticated is True
        assert "Authorization" in ctx.headers
        assert ctx.headers["Authorization"] == "Bearer test-key-123"

    def test_api_key_missing(self) -> None:
        """API キー未設定は認証失敗"""
        proxy = AuthProxy()
        proxy.configure_server(ServerAuthConfig(
            server_name="broken",
            mode=AuthMode.API_KEY,
            api_key=None,
        ))
        ctx = proxy.authenticate("broken")
        assert ctx.authenticated is False

    def test_oauth2_not_implemented(self) -> None:
        """OAuth 2.1 は NotImplementedError"""
        proxy = AuthProxy()
        proxy.configure_server(ServerAuthConfig(
            server_name="oauth_server",
            mode=AuthMode.OAUTH2,
        ))
        with pytest.raises(NotImplementedError):
            proxy.authenticate("oauth_server")

    def test_configured_servers(self) -> None:
        """設定済みサーバーリスト"""
        proxy = AuthProxy()
        proxy.configure_server(ServerAuthConfig(server_name="a", mode=AuthMode.PASSTHROUGH))
        proxy.configure_server(ServerAuthConfig(server_name="b", mode=AuthMode.API_KEY, api_key="x"))
        assert sorted(proxy.get_configured_servers()) == ["a", "b"]


# =============================================================================
# VirtualServer テスト
# =============================================================================

class TestVirtualServer:
    """Virtual MCP Server のテスト"""

    @pytest.fixture
    def gateway(self) -> VirtualServer:
        """テスト用 Gateway をセットアップ"""
        discovery = DiscoveryEngine()
        discovery.register_local_defaults()
        enforcer = PolicyEnforcer()
        auth = AuthProxy()
        vs = VirtualServer(discovery, enforcer, auth)
        vs.register_tool("gnosis", "search", "知識検索")
        vs.register_tool("sophia", "search", "KI検索")
        return vs

    def test_route_success(self, gateway: VirtualServer) -> None:
        """正常ルーティング"""
        result = gateway.route("gnosis.search")
        assert result.success is True
        assert result.server_info is not None
        assert result.server_info.name == "gnosis"
        assert result.tool_name == "search"

    def test_route_invalid_namespace(self, gateway: VirtualServer) -> None:
        """無効な名前空間"""
        result = gateway.route("invalid_no_dot")
        assert result.success is False
        assert result.error is not None
        assert result.error.code == "INVALID_NAMESPACE"

    def test_route_unknown_server(self, gateway: VirtualServer) -> None:
        """未登録サーバー"""
        result = gateway.route("unknown.tool")
        assert result.success is False
        assert result.error is not None
        assert result.error.code == "SERVER_NOT_FOUND"

    def test_route_destructive_blocked(self, gateway: VirtualServer) -> None:
        """破壊的操作がブロックされる"""
        result = gateway.route("gnosis.delete_all")
        assert result.success is False
        assert result.error is not None
        assert result.error.code == "APPROVAL_REQUIRED"

    def test_tool_listing(self, gateway: VirtualServer) -> None:
        """ツール一覧"""
        tools = gateway.list_tools()
        assert len(tools) == 2
        names = {t.namespaced_name for t in tools}
        assert "gnosis.search" in names
        assert "sophia.search" in names

    def test_tools_by_server(self, gateway: VirtualServer) -> None:
        """サーバー別ツール一覧"""
        tools = gateway.list_tools_by_server("gnosis")
        assert len(tools) == 1
        assert tools[0].tool_name == "search"

    def test_gateway_status(self, gateway: VirtualServer) -> None:
        """ステータス表示"""
        status = gateway.get_status()
        assert status["servers_registered"] == 9
        assert status["tools_registered"] == 2
        assert status["policies_loaded"] > 0
        assert "gnosis" in status["servers"]

    def test_register_server_tools_batch(self, gateway: VirtualServer) -> None:
        """一括ツール登録"""
        count = gateway.register_server_tools("hermeneus", ["dispatch", "compile", "execute"])
        assert count == 3
        tools = gateway.list_tools_by_server("hermeneus")
        assert len(tools) == 3


# =============================================================================
# 統合テスト
# =============================================================================

class TestGatewayIntegration:
    """4コンポーネント統合テスト"""

    def test_full_pipeline(self) -> None:
        """Discovery → Register → Policy → Auth → Route の全パイプライン"""
        # 1. Discovery
        discovery = DiscoveryEngine()
        discovery.register_local_defaults()
        assert discovery.server_count == 9

        # 2. Policy
        enforcer = PolicyEnforcer()
        assert enforcer.policy_count > 0

        # 3. Auth
        auth = AuthProxy()

        # 4. Virtual Server
        vs = VirtualServer(discovery, enforcer, auth)
        vs.register_tool("gnosis", "search")
        vs.register_tool("hermeneus", "dispatch")

        # 正常ルーティング
        result = vs.route("gnosis.search")
        assert result.success is True

        # 破壊的操作ブロック
        result = vs.route("gnosis.delete_everything")
        assert result.success is False

        # 未知サーバーブロック
        result = vs.route("evil.steal_data")
        assert result.success is False

        # ステータス確認
        status = vs.get_status()
        assert status["servers_registered"] == 9
        assert status["tools_registered"] == 2
