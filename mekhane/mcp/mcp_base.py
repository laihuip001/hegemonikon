#!/usr/bin/env python3
"""
MCP Base Module — Hegemonikón MCP Server Common Infrastructure

All MCP servers share:
  - StdoutSuppressor: prevent stdout pollution during imports
  - log(): stderr-only logging with server name prefix
  - path setup: project root calculation
  - MCP SDK imports
  - main() / run loop boilerplate
  - error handling wrapper for call_tool

Usage:
    from mcp_base import MCPBase, StdoutSuppressor

    base = MCPBase("server_name", "1.0.0", "Description")
    server = base.server
    log = base.log

    @server.list_tools()
    async def list_tools(): ...

    @server.call_tool()
    async def call_tool(name, arguments):
        async with base.tool_guard(name):
            ...

    if __name__ == "__main__":
        base.run()
"""

import sys
import io
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

# Platform-specific asyncio setup
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Preserve original stdout before any redirection
_original_stdout = sys.stdout


class StdoutSuppressor:
    """Suppress stdout during imports to prevent MCP protocol pollution.

    MCP uses stdio for JSON-RPC. Any stray print() call will corrupt
    the protocol stream. This context manager redirects stdout to
    a StringIO buffer during the suppressed block.
    """

    def __init__(self):
        self._null = io.StringIO()
        self._old_stdout = None

    def __enter__(self):
        self._old_stdout = sys.stdout
        sys.stdout = self._null
        return self

    def __exit__(self, *args):
        sys.stdout = self._old_stdout
        captured = self._null.getvalue()
        if captured.strip():
            print(
                f"[mcp-base] Suppressed stdout: {captured[:200]}...",
                file=sys.stderr,
                flush=True,
            )


class MCPBase:
    """Common infrastructure for all Hegemonikón MCP servers.

    Handles:
      - Logging (stderr only)
      - Path setup (project root discovery)
      - Server initialization
      - Error-safe tool execution
      - Main run loop
    """

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

    def _setup_paths(self):
        """Add project root and mekhane dir to sys.path."""
        # mekhane/mcp/mcp_base.py → mekhane/ → hegemonikon/
        self.mcp_dir = Path(__file__).parent
        self.mekhane_dir = self.mcp_dir.parent
        self.project_root = self.mekhane_dir.parent

        for p in [str(self.project_root), str(self.mekhane_dir)]:
            if p not in sys.path:
                sys.path.insert(0, p)

    def _log(self, msg: str):
        """Log to stderr with server name prefix."""
        print(f"[{self.name}] {msg}", file=sys.stderr, flush=True)

    @property
    def log(self):
        """Provide log function for external use."""
        return self._log

    @asynccontextmanager
    async def tool_guard(self, tool_name: str):
        """Context manager for safe tool execution with error handling.

        Usage:
            async with base.tool_guard("my_tool"):
                # tool logic here
                return [TextContent(type="text", text="result")]
        """
        self._log(f"call_tool: {tool_name}")
        try:
            yield
        except Exception as e:
            self._log(f"Error in {tool_name}: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            # Note: caller must handle the return value

    def error_response(self, msg: str):
        """Create a standard error response."""
        return [self.TextContent(type="text", text=f"Error: {msg}")]

    def text_response(self, text: str):
        """Create a standard text response."""
        return [self.TextContent(type="text", text=text)]

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
