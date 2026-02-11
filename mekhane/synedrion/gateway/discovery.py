# PROOF: [L2/インフラ] <- mekhane/synedrion/gateway/ A0→MCPサーバー発見が必要→DiscoveryEngineが担う
"""
Discovery Engine — MCP サーバーの自動発見と手動登録

SEP-1960 .well-known/mcp プローブによるリモートサーバー発見と、
ローカル (stdio) サーバーの手動登録を統合する。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TransportType(Enum):
    """MCP トランスポート種別"""
    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable-http"
    SSE = "sse"


@dataclass
class ServerInfo:
    """MCP サーバー情報"""
    name: str
    transport: TransportType
    command: str | None = None        # stdio の場合
    url: str | None = None            # HTTP の場合
    mcp_version: str = "2024-11-05"
    tools: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    auth_type: str | None = None      # "oauth2", "api_key", None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_local(self) -> bool:
        return self.transport == TransportType.STDIO

    @property
    def is_remote(self) -> bool:
        return self.transport in (TransportType.STREAMABLE_HTTP, TransportType.SSE)


class DiscoveryEngine:
    """
    MCP サーバーの発見・登録を管理する。

    使用例:
        engine = DiscoveryEngine()

        # ローカルサーバーの手動登録
        engine.register(ServerInfo(
            name="gnosis",
            transport=TransportType.STDIO,
            command="python mekhane/mcp/gnosis_mcp_server.py",
        ))

        # リモートサーバーの発見 (SEP-1960)
        info = await engine.discover("https://example.com")

        # 一覧
        for name, info in engine.servers.items():
            print(f"{name}: {info.transport.value}")
    """

    def __init__(self) -> None:
        self._servers: dict[str, ServerInfo] = {}

    def register(self, server: ServerInfo) -> None:
        """ローカルサーバーを手動登録する"""
        if server.name in self._servers:
            logger.info("Updating server registration: %s", server.name)
        else:
            logger.info("Registering server: %s (%s)", server.name, server.transport.value)
        self._servers[server.name] = server

    def unregister(self, name: str) -> bool:
        """サーバー登録を解除する"""
        if name in self._servers:
            del self._servers[name]
            logger.info("Unregistered server: %s", name)
            return True
        return False

    async def discover(self, base_url: str) -> ServerInfo | None:
        """
        SEP-1960 .well-known/mcp プローブでリモートサーバーを発見する。

        Args:
            base_url: サーバーのベース URL (例: "https://example.com")

        Returns:
            ServerInfo if discovered, None if not available
        """
        try:
            import httpx
        except ImportError:
            logger.warning("httpx not installed — remote discovery unavailable")
            return None

        well_known_url = f"{base_url.rstrip('/')}/.well-known/mcp"
        logger.info("Probing %s", well_known_url)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(well_known_url)

            if response.status_code != 200:
                logger.info("No .well-known/mcp at %s (status: %d)", base_url, response.status_code)
                return None

            data = response.json()
            capabilities = data.get("capabilities", {})
            auth = data.get("authentication", {})

            # トランスポート推定
            transport = TransportType.STREAMABLE_HTTP
            if "sse" in data.get("transport", ""):
                transport = TransportType.SSE

            # サーバー名の抽出
            name = data.get("name", base_url.split("//")[-1].split("/")[0])

            info = ServerInfo(
                name=name,
                transport=transport,
                url=base_url,
                mcp_version=data.get("mcpVersion", "2024-11-05"),
                tools=list(capabilities.get("tools", {}).keys()) if isinstance(capabilities.get("tools"), dict) else [],
                resources=list(capabilities.get("resources", {}).keys()) if isinstance(capabilities.get("resources"), dict) else [],
                auth_type=auth.get("type"),
                metadata=data,
            )

            self.register(info)
            logger.info("Discovered server: %s (%d tools)", name, len(info.tools))
            return info

        except Exception as e:
            logger.warning("Discovery failed for %s: %s", base_url, e)
            return None

    def get(self, name: str) -> ServerInfo | None:
        """名前でサーバー情報を取得"""
        return self._servers.get(name)

    @property
    def servers(self) -> dict[str, ServerInfo]:
        """全登録サーバーの辞書 (読取専用コピー)"""
        return dict(self._servers)

    @property
    def server_count(self) -> int:
        return len(self._servers)

    def register_local_defaults(self) -> int:
        """
        HGK の標準ローカルサーバーを一括登録する。

        Returns:
            登録したサーバー数
        """
        defaults = [
            ServerInfo(name="gnosis", transport=TransportType.STDIO,
                       command="python mekhane/mcp/gnosis_mcp_server.py"),
            ServerInfo(name="sophia", transport=TransportType.STDIO,
                       command="python mekhane/mcp/sophia_mcp_server.py"),
            ServerInfo(name="hermeneus", transport=TransportType.STDIO,
                       command="python hermeneus/src/mcp_server.py"),
            ServerInfo(name="sympatheia", transport=TransportType.STDIO,
                       command="python mekhane/mcp/sympatheia_mcp_server.py"),
            ServerInfo(name="mneme", transport=TransportType.STDIO,
                       command="python mekhane/mcp/mneme_server.py"),
            ServerInfo(name="digestor", transport=TransportType.STDIO,
                       command="python mekhane/mcp/digestor_mcp_server.py"),
            ServerInfo(name="jules", transport=TransportType.STDIO,
                       command="python mekhane/mcp/jules_mcp_server.py"),
            ServerInfo(name="prompt-lang", transport=TransportType.STDIO,
                       command="python mekhane/mcp/prompt_lang_mcp_server.py"),
            ServerInfo(name="sequential-thinking", transport=TransportType.STDIO,
                       command="npx -y @anthropic/mcp-sequential-thinking"),
        ]
        for server in defaults:
            self.register(server)
        return len(defaults)
