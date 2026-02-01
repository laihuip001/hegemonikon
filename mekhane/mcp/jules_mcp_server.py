# PROOF: [L2/インフラ] A0→MCP経由のアクセスが必要→jules_mcp_server が担う
#!/usr/bin/env python3
"""
Jules MCP Server - Hegemonikón H3 Symplokē Layer

Model Context Protocol server for Jules API integration.
Exposes jules_create_task, jules_batch_execute, jules_get_status tools.

CRITICAL: This file follows MCP stdio protocol rules:
- stdout: JSON-RPC messages ONLY
- stderr: All logging and debug output
"""

import sys
import os

# ============ Platform-specific asyncio setup ============
if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ Redirect stdout to stderr for logging ============
import io


def log(msg):
    print(f"[jules-mcp] {msg}", file=sys.stderr, flush=True)


log("Starting Jules MCP Server...")

# ============ Import path setup ============
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ============ Import MCP SDK ============
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent

    log("MCP imports successful")
except ImportError as e:
    log(f"MCP SDK not installed: {e}")
    log("Install with: pip install mcp")
    sys.exit(1)

# ============ Initialize MCP Server ============
server = Server(
    name="jules",
    version="1.0.0",
    instructions="Jules API integration for parallel code generation tasks",
)
log("Server initialized")


@server.list_tools()
async def list_tools():
    """List available Jules tools."""
    log("list_tools called")
    return [
        Tool(
            name="jules_create_task",
            description="Create a single Jules code generation task. Returns session ID for tracking.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Task description (e.g., 'Fix bug in utils.py')",
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/repo'",
                    },
                    "branch": {
                        "type": "string",
                        "description": "Starting branch (default: main)",
                        "default": "main",
                    },
                },
                "required": ["prompt", "repo"],
            },
        ),
        Tool(
            name="jules_get_status",
            description="Get status of a Jules session by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID from jules_create_task",
                    }
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="jules_batch_execute",
            description="Execute multiple Jules tasks in parallel (max 30 concurrent). Waits for all to complete.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "description": "List of task objects with 'prompt', 'repo', optional 'branch'",
                        "items": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string"},
                                "repo": {"type": "string"},
                                "branch": {"type": "string"},
                            },
                            "required": ["prompt", "repo"],
                        },
                    },
                    "max_concurrent": {
                        "type": "integer",
                        "description": "Maximum concurrent sessions (default: 30, max: 60)",
                        "default": 30,
                    },
                },
                "required": ["tasks"],
            },
        ),
        Tool(
            name="jules_list_repos",
            description="List available GitHub repositories connected to Jules.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool(validate_input=True)
async def call_tool(name: str, arguments: dict):
    """Handle Jules tool calls."""
    log(f"call_tool: {name} with {arguments}")

    # Lazy import to avoid startup overhead
    try:
        from mekhane.symploke.jules_client import JulesClient, SessionState
    except ImportError as e:
        return [
            TextContent(type="text", text=f"Error: Jules client not available: {e}")
        ]

    # Get API key from environment
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        return [
            TextContent(
                type="text", text="Error: JULES_API_KEY environment variable not set"
            )
        ]

    try:
        client = JulesClient(api_key)
    except Exception as e:
        return [TextContent(type="text", text=f"Error initializing client: {e}")]

    # ============ jules_create_task ============
    if name == "jules_create_task":
        prompt = arguments.get("prompt", "")
        repo = arguments.get("repo", "")
        branch = arguments.get("branch", "main")

        if not prompt or not repo:
            return [
                TextContent(type="text", text="Error: prompt and repo are required")
            ]

        try:
            source = f"sources/github/{repo}"
            session = await client.create_session(prompt, source, branch)

            output = f"""# Jules Task Created

- **Session ID**: `{session.id}`
- **State**: {session.state.value}
- **Repository**: {repo}
- **Branch**: {branch}

Use `jules_get_status` with session_id to check progress.
"""
            log(f"Created session: {session.id}")
            return [TextContent(type="text", text=output)]

        except Exception as e:
            log(f"Error creating session: {e}")
            return [TextContent(type="text", text=f"Error: {e}")]

    # ============ jules_get_status ============
    elif name == "jules_get_status":
        session_id = arguments.get("session_id", "")

        if not session_id:
            return [TextContent(type="text", text="Error: session_id is required")]

        try:
            session = await client.get_session(session_id)

            status_emoji = {
                SessionState.PLANNING: "📝",
                SessionState.IMPLEMENTING: "🔨",
                SessionState.TESTING: "🧪",
                SessionState.COMPLETED: "✅",
                SessionState.FAILED: "❌",
            }

            output = f"""# Jules Session Status

- **Session ID**: `{session.id}`
- **State**: {status_emoji.get(session.state, "❓")} {session.state.value}
"""
            if session.pull_request_url:
                output += f"- **Pull Request**: {session.pull_request_url}\n"
            if session.error:
                output += f"- **Error**: {session.error}\n"

            log(f"Session {session_id}: {session.state.value}")
            return [TextContent(type="text", text=output)]

        except Exception as e:
            log(f"Error getting status: {e}")
            return [TextContent(type="text", text=f"Error: {e}")]

    # ============ jules_batch_execute ============
    elif name == "jules_batch_execute":
        tasks = arguments.get("tasks", [])
        max_concurrent = min(arguments.get("max_concurrent", 30), 60)

        if not tasks:
            return [TextContent(type="text", text="Error: tasks list is required")]

        try:
            # Convert repo format
            formatted_tasks = []
            for task in tasks:
                formatted_tasks.append(
                    {
                        "prompt": task["prompt"],
                        "source": f"sources/github/{task['repo']}",
                        "branch": task.get("branch", "main"),
                    }
                )

            log(f"Executing {len(tasks)} tasks with max_concurrent={max_concurrent}")
            results = await client.batch_execute(formatted_tasks, max_concurrent)

            # Format results
            output_lines = [f"# Jules Batch Results\n"]
            output_lines.append(f"**Total**: {len(results)} tasks\n")

            completed = sum(1 for r in results if r.state == SessionState.COMPLETED)
            failed = sum(1 for r in results if r.state == SessionState.FAILED)
            output_lines.append(f"- ✅ Completed: {completed}")
            output_lines.append(f"- ❌ Failed: {failed}\n")

            for i, result in enumerate(results, 1):
                emoji = "✅" if result.state == SessionState.COMPLETED else "❌"
                output_lines.append(f"## [{i}] {emoji} {result.prompt[:50]}...")
                if result.pull_request_url:
                    output_lines.append(f"- PR: {result.pull_request_url}")
                if result.error:
                    output_lines.append(f"- Error: {result.error}")
                output_lines.append("")

            log(f"Batch complete: {completed}/{len(results)} succeeded")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Batch execution error: {e}")
            return [TextContent(type="text", text=f"Error: {e}")]

    # ============ jules_list_repos ============
    elif name == "jules_list_repos":
        # Note: This would require implementing the sources endpoint
        return [
            TextContent(
                type="text",
                text="""# Jules Repositories

Repository listing not yet implemented.
Use repository format: `owner/repo` (e.g., `laihuip001/hegemonikon`)
""",
            )
        ]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    log("Starting stdio server...")
    try:
        async with stdio_server() as streams:
            log("stdio_server connected")
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )
    except Exception as e:
        log(f"Server error: {e}")
        raise


if __name__ == "__main__":
    import asyncio

    # Check for test mode
    if "--test" in sys.argv:
        print("Jules MCP Server Test")
        print("-" * 40)
        api_key = os.environ.get("JULES_API_KEY")
        if api_key:
            print(f"✅ JULES_API_KEY: {api_key[:8]}...{api_key[-4:]}")
        else:
            print("⚠️  JULES_API_KEY not set")
        print("✅ Server module loaded successfully")
    else:
        log("Running main...")
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            log("Server stopped by user")
        except Exception as e:
            log(f"Fatal error: {e}")
            sys.exit(1)
