#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/mcp/mcp_base
"""
PROOF: [L2/インフラ]

P3 → 知識収集が必要
   → MCP サーバーの基盤が必要
   → mcp_base が担う

Q.E.D.

---

MCP Base Module — Hegemonikón MCP Server Common Infrastructure

All MCP servers share:
  - StdoutSuppressor: prevent stdout pollution during imports
  - log(): stderr-only logging with server name prefix
  - path setup: project root calculation
  - MCP SDK imports (Tool, TextContent, Server, stdio_server)
  - main() / run loop boilerplate

Usage:
    from mcp_base import MCPBase, StdoutSuppressor

    base = MCPBase("server_name", "1.0.0", "Description")
    server = base.server
    log = base.log

    @server.list_tools()
    async def list_tools(): ...

    @server.call_tool()
    async def call_tool(name, arguments): ...

    if __name__ == "__main__":
        base.run()
"""

import sys
import io
import asyncio
from pathlib import Path


# Platform-specific asyncio setup
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Preserve original stdout before any redirection
_original_stdout = sys.stdout


# PURPOSE: 標準出力の抑制
class StdoutSuppressor:
    """Suppress stdout during imports to prevent MCP protocol pollution.

    MCP uses stdio for JSON-RPC. Any stray print() call will corrupt
    the protocol stream. This context manager redirects stdout to
    a StringIO buffer during the suppressed block.
    """

    # PURPOSE: 初期化
    def __init__(self):
        self._null = io.StringIO()
        self._old_stdout = None

    # PURPOSE: enter処理
    def __enter__(self):
        self._old_stdout = sys.stdout
        sys.stdout = self._null
        return self

    # PURPOSE: exit処理
    def __exit__(self, *args):
        sys.stdout = self._old_stdout
        captured = self._null.getvalue()
        if captured.strip():
            print(
                f"[mcp-base] Suppressed stdout: {captured[:200]}...",
                file=sys.stderr,
                flush=True,
            )


# PURPOSE: MCP基底クラス
class MCPBase:
    """Common infrastructure for all Hegemonikón MCP servers.

    Handles:
      - Logging (stderr only)
      - Path setup (project root discovery)
      - Server initialization
      - Error-safe tool execution
      - Main run loop
    """

    # PURPOSE: 初期化
    def __init__(self, name: str, version: str, instructions: str):
        self.name = name
        self.version = version
        self._setup_paths()
        self._log(f"Starting {name} MCP Server v{version}...")

        # Import MCP SDK
        try:
            from mcp.server import Server
            from mcp.server.stdio import stdio_server
            from mcp.types import Tool, TextContent

            self._stdio_server = stdio_server
            self.Tool = Tool
            self.TextContent = TextContent
            self._log("MCP SDK imports OK")
        except Exception as e:
            self._log(f"MCP SDK import error: {e}")
            sys.exit(1)

        # Create server instance
        self.server = Server(
            name=name,
            version=version,
            instructions=instructions,
        )
        self._log("Server initialized")

    # PURPOSE: パスのセットアップ
    def _setup_paths(self):
        """Add project root and mekhane dir to sys.path."""
        # mekhane/mcp/mcp_base.py → mekhane/ → hegemonikon/
        self.mcp_dir = Path(__file__).parent
        self.mekhane_dir = self.mcp_dir.parent
        self.project_root = self.mekhane_dir.parent

        for p in [str(self.project_root), str(self.mekhane_dir)]:
            if p not in sys.path:
                sys.path.insert(0, p)

    # PURPOSE: ログ出力
    def _log(self, msg: str):
        """Log to stderr with server name prefix."""
        print(f"[{self.name}] {msg}", file=sys.stderr, flush=True)

    # PURPOSE: logプロパティ
    @property
    def log(self):
        """Provide log function for external use."""
        return self._log



    # PURPOSE: メインループ
    async def _main(self):
        """MCP server main loop."""
        self._log("Starting stdio server...")
        try:
            async with self._stdio_server() as streams:
                self._log("stdio connected")
                await self.server.run(
                    streams[0],
                    streams[1],
                    self.server.create_initialization_options(),
                )
        except Exception as e:
            self._log(f"Server error: {e}")
            raise

    # PURPOSE: サーバー実行
    def run(self):
        """Run the MCP server (blocking)."""
        self._log("Running main...")
        try:
            asyncio.run(self._main())
        except KeyboardInterrupt:
            self._log("Stopped by user")
        except Exception as e:
            self._log(f"Fatal error: {e}")
            sys.exit(1)
