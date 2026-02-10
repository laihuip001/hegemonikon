"""
Auth Proxy — MCP Gateway の認証委譲

現在はパススルーモード (認証なし) がデフォルト。
将来の OAuth 2.1 統合のための骨格を提供する。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AuthMode(Enum):
    """認証モード"""
    PASSTHROUGH = "passthrough"    # 認証なし (デフォルト)
    API_KEY = "api_key"           # API キー認証
    OAUTH2 = "oauth2"            # OAuth 2.1 (将来)


@dataclass
class AuthContext:
    """認証コンテキスト — リクエストに付与される認証情報"""
    mode: AuthMode = AuthMode.PASSTHROUGH
    headers: dict[str, str] = field(default_factory=dict)
    server_name: str = ""
    authenticated: bool = False

    @property
    def is_passthrough(self) -> bool:
        return self.mode == AuthMode.PASSTHROUGH


@dataclass
class ServerAuthConfig:
    """サーバーごとの認証設定"""
    server_name: str
    mode: AuthMode = AuthMode.PASSTHROUGH
    api_key: str | None = None
    oauth_config: dict[str, Any] | None = None


class AuthProxy:
    """
    MCP Gateway の認証プロキシ。

    パススルーがデフォルト。サーバーごとに認証モードを設定可能。

    使用例:
        proxy = AuthProxy()

        # パススルー (デフォルト)
        ctx = proxy.authenticate("gnosis")
        assert ctx.is_passthrough

        # API キーを設定
        proxy.configure_server(ServerAuthConfig(
            server_name="external_api",
            mode=AuthMode.API_KEY,
            api_key="sk-...",
        ))
        ctx = proxy.authenticate("external_api")
        assert "Authorization" in ctx.headers
    """

    def __init__(self) -> None:
        self._configs: dict[str, ServerAuthConfig] = {}

    def configure_server(self, config: ServerAuthConfig) -> None:
        """サーバーの認証設定を登録する"""
        self._configs[config.server_name] = config
        logger.info("Auth configured for %s: %s", config.server_name, config.mode.value)

    def authenticate(self, server_name: str) -> AuthContext:
        """
        サーバーへのリクエストの認証コンテキストを生成する。

        Args:
            server_name: 対象サーバー名

        Returns:
            AuthContext: 認証情報 (ヘッダー含む)
        """
        config = self._configs.get(server_name)

        if config is None or config.mode == AuthMode.PASSTHROUGH:
            return AuthContext(
                mode=AuthMode.PASSTHROUGH,
                server_name=server_name,
                authenticated=True,  # パススルーは常に「認証済み」
            )

        if config.mode == AuthMode.API_KEY:
            return self._auth_api_key(config)

        if config.mode == AuthMode.OAUTH2:
            return self._auth_oauth2(config)

        return AuthContext(
            mode=AuthMode.PASSTHROUGH,
            server_name=server_name,
            authenticated=True,
        )

    def _auth_api_key(self, config: ServerAuthConfig) -> AuthContext:
        """API キー認証"""
        if not config.api_key:
            logger.warning("API key not set for %s", config.server_name)
            return AuthContext(
                mode=AuthMode.API_KEY,
                server_name=config.server_name,
                authenticated=False,
            )

        return AuthContext(
            mode=AuthMode.API_KEY,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "X-Upstream-Authorization": f"Bearer {config.api_key}",
            },
            server_name=config.server_name,
            authenticated=True,
        )

    def _auth_oauth2(self, config: ServerAuthConfig) -> AuthContext:
        """
        OAuth 2.1 認証 — 将来実装。

        現在は NotImplementedError を raise する。
        実装時は token refresh, scope 制限, PKCE を含む。
        """
        raise NotImplementedError(
            "OAuth 2.1 authentication is not yet implemented. "
            "This is a planned feature for the MCP Gateway. "
            f"Server: {config.server_name}"
        )

    def get_configured_servers(self) -> list[str]:
        """認証設定済みのサーバー一覧"""
        return list(self._configs.keys())

    @property
    def config_count(self) -> int:
        return len(self._configs)
