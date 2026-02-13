# PROOF: [L2/インフラ] <- mekhane/mcp/ Ochēma MCP Server
#!/usr/bin/env python3
"""
Ochēma MCP Server — Antigravity Language Server Bridge

Antigravity IDE の Language Server を介して LLM テキスト生成を行う
MCP サーバ。4-Step API フロー (StartCascade → SendMessage →
GetTrajectories → GetSteps) をMCP tool として公開する。

CRITICAL: This file follows MCP stdio protocol rules:
- stdout: JSON-RPC messages ONLY
- stderr: All logging and debug output

WARNING: ToS グレーゾーン。実験用途限定。公開禁止。
"""

import sys
import os

# ============ CRITICAL: Platform-specific asyncio setup ============
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ CRITICAL: Redirect ALL stdout to stderr ============
import io

_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr


# Debug logging to stderr
# PURPOSE: log — MCP サービスの処理
def log(msg):
    print(f"[ochema-mcp] {msg}", file=sys.stderr, flush=True)


log("Starting Ochēma MCP Server...")
log(f"Python: {sys.executable}")

# ============ Import path setup ============
from pathlib import Path

# mekhane/mcp/ → mekhane/ → hegemonikon/ (project root)
_mekhane_dir = Path(__file__).parent.parent
_project_root = _mekhane_dir.parent
for _p in [str(_project_root), str(_mekhane_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
log(f"Added to path: {_project_root}")


# ============ Suppress stdout during imports ============
# PURPOSE: クラス: StdoutSuppressor
class StdoutSuppressor:
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
            log(f"Suppressed stdout: {captured[:100]}...")


# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent

    log("MCP imports successful")
except Exception as e:
    log(f"MCP import error: {e}")
    sys.exit(1)

# Initialize MCP server
server = Server(
    name="ochema",
    version="0.1.0",
    instructions=(
        "Ochēma — Antigravity Language Server bridge. "
        "Send prompts to LLM (Claude/Gemini) via local Language Server. "
        "Also provides status and model listing."
    ),
)
log("Server initialized")

# Lazy-loaded client instance
_client = None


# PURPOSE: get_client — AntigravityClient のシングルトン取得
def get_client():
    """AntigravityClient をシングルトンで取得。"""
    global _client
    if _client is None:
        try:
            with StdoutSuppressor():
                from mekhane.ochema.antigravity_client import AntigravityClient
            _client = AntigravityClient()
            log(f"Client initialized: PID={_client.pid} Port={_client.port}")
        except Exception as e:
            log(f"Client init error: {e}")
            raise
    return _client


@server.list_tools()
async def list_tools():
    """List available tools."""
    log("list_tools called")
    return [
        Tool(
            name="ask",
            description=(
                "Send a prompt to an LLM via Antigravity Language Server. "
                "Returns the LLM response text, thinking process, and model info. "
                "Available models: Claude Sonnet 4.5 Thinking (default), "
                "Claude Opus 4.6 Thinking, Gemini 2.5 Pro, Gemini 2.5 Flash, GPT-4.1."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The prompt to send to the LLM",
                    },
                    "model": {
                        "type": "string",
                        "description": (
                            "Model enum string. Defaults to MODEL_CLAUDE_4_5_SONNET_THINKING. "
                            "Options: MODEL_CLAUDE_4_5_SONNET_THINKING, "
                            "MODEL_PLACEHOLDER_M26 (Opus 4.6), "
                            "MODEL_GEMINI_2_5_PRO, MODEL_GEMINI_2_5_FLASH, MODEL_GPT_4_1"
                        ),
                        "default": "MODEL_CLAUDE_4_5_SONNET_THINKING",
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Max wait seconds for LLM response (default: 120)",
                        "default": 120,
                    },
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="status",
            description="Get Language Server connection status and quota info.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="models",
            description="List available LLM models with remaining quota percentages.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool(validate_input=True)
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    log(f"call_tool: {name} with {arguments}")

    if name == "ask":
        message = arguments.get("message", "")
        model = arguments.get("model", "MODEL_CLAUDE_4_5_SONNET_THINKING")
        timeout = arguments.get("timeout", 120)

        if not message:
            return [TextContent(type="text", text="Error: message is required")]

        try:
            client = get_client()
            log(f"Sending to {model}: {message[:50]}...")

            response = client.ask(message, model=model, timeout=timeout)

            output_lines = [
                "# Ochēma LLM Response\n",
                f"**Model**: {response.model}",
                f"**Cascade ID**: {response.cascade_id[:16]}...",
                "",
                "## Response\n",
                response.text,
            ]

            if response.thinking:
                output_lines.extend([
                    "",
                    "## Thinking\n",
                    response.thinking[:1000],
                ])

            if response.token_usage:
                output_lines.extend([
                    "",
                    "## Token Usage\n",
                    f"```json\n{response.token_usage}\n```",
                ])

            log(f"Response received: {len(response.text)} chars")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except TimeoutError as e:
            log(f"Timeout: {e}")
            return [TextContent(type="text", text=f"Error: LLM response timed out ({timeout}s)")]
        except Exception as e:
            log(f"Ask error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "status":
        try:
            client = get_client()
            status = client.get_status()

            user_status = status.get("userStatus", {})
            output_lines = [
                "# Ochēma Status\n",
                f"- **PID**: {client.pid}",
                f"- **Port**: {client.port}",
                f"- **Workspace**: {client.workspace}",
                f"- **Name**: {user_status.get('name', 'N/A')}",
            ]

            log("Status returned")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Status error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "models":
        try:
            client = get_client()
            models = client.list_models()

            output_lines = ["# Available Models\n"]
            output_lines.append("| Model | Label | Remaining |")
            output_lines.append("|:------|:------|----------:|")
            for m in models:
                output_lines.append(
                    f"| `{m['name']}` | {m['label']} | {m['remaining']}% |"
                )

            log(f"Models listed: {len(models)}")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Models error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# PURPOSE: ochema_mcp_server の main 処理を実行する
async def main():
    """Run the MCP server."""
    log("Starting stdio server...")
    try:
        async with stdio_server() as streams:
            log("stdio_server connected")
            await server.run(
                streams[0],
                streams[1],
                server.create_initialization_options(),
            )
    except Exception as e:
        log(f"Server error: {e}")
        raise


if __name__ == "__main__":
    import asyncio

    log("Running main...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Server stopped by user")
    except Exception as e:
        log(f"Fatal error: {e}")
        sys.exit(1)
