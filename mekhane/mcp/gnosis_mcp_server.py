# PROOF: [L2/インフラ] <- mekhane/mcp/ A0→MCP経由のアクセスが必要→gnosis_mcp_server が担う
#!/usr/bin/env python3
"""
Gnōsis MCP Server - Hegemonikón Knowledge Base

Model Context Protocol server for academic paper search.
Exposes search and stats tools via stdio transport.

CRITICAL: This file follows MCP stdio protocol rules:
- stdout: JSON-RPC messages ONLY
- stderr: All logging and debug output
"""

import sys
import os

# ============ CRITICAL: Platform-specific asyncio setup ============
# Must be done BEFORE any other imports that might use asyncio
if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ CRITICAL: Redirect ALL stdout to stderr ============
# This prevents any accidental stdout pollution from imported modules
import io

_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr


# Debug logging to stderr (won't interfere with MCP stdio)
# PURPOSE: log — MCPサービスの処理
def log(msg):
    print(f"[gnosis-mcp] {msg}", file=sys.stderr, flush=True)


log("Starting Gnōsis MCP Server...")
log(f"Python: {sys.executable}")
log(f"Platform: {sys.platform}")

# ============ Import path setup ============
from pathlib import Path

# mekhane/mcp/ → mekhane/ → hegemonikon/ (project root)
_mekhane_dir = Path(__file__).parent.parent
_project_root = _mekhane_dir.parent
for _p in [str(_project_root), str(_mekhane_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
log(f"Added to path: {_project_root} + {_mekhane_dir}")


# ============ Suppress stdout during imports ============
# Some libraries (like lancedb) print to stdout during import
# PURPOSE: クラス: StdoutSuppressor
class StdoutSuppressor:
    # PURPOSE: StdoutSuppressor の構成と依存関係の初期化
    def __init__(self):
        self._null = io.StringIO()
        self._old_stdout = None

    # PURPOSE: enter__ — MCPサービスの内部処理
    def __enter__(self):
        self._old_stdout = sys.stdout
        sys.stdout = self._null
        return self

    # PURPOSE: exit__ — MCPサービスの内部処理
    def __exit__(self, *args):
        sys.stdout = self._old_stdout
        captured = self._null.getvalue()
        if captured.strip():
            log(f"Suppressed stdout during import: {captured[:100]}...")


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
    name="gnosis",
    version="1.0.0",
    instructions="Gnōsis knowledge base for academic paper search",
)
log("Server initialized")
# PURPOSE: List available tools.


@server.list_tools()
# PURPOSE: [L2-auto] List available tools.
async def list_tools():
    """List available tools."""
    log("list_tools called")
    return [
        Tool(
            name="search",
            description="Search the Gnōsis knowledge base for academic papers. Returns relevant papers with titles, authors, abstracts, and citations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'transformer attention mechanism')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="stats",
            description="Get statistics about the Gnōsis knowledge base (total papers, sources, etc.)",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="recommend_model",
            description="Recommend the best AI model (Claude/Gemini) for a given task based on T2 Krisis priority rules (P1-P5). Returns model recommendation with detected keywords and reasoning.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Description of the task to analyze (e.g., 'UI design for dashboard', 'security audit of API')",
                    }
                },
                "required": ["task_description"],
            },
        ),
    ]
# PURPOSE: tool calls の安全な処理を保証する


@server.call_tool(validate_input=True)
# PURPOSE: [L2-auto] Handle tool calls.
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    log(f"call_tool: {name} with {arguments}")

    if name == "search":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 5)

        if not query:
            return [TextContent(type="text", text="Error: query is required")]

        try:
            # Lazy import with stdout suppression
            with StdoutSuppressor():
                from mekhane.anamnesis.index import GnosisIndex

            log(f"Searching for: {query}")
            index = GnosisIndex()
            results = index.search(query, k=limit)

            if not results:
                return [TextContent(type="text", text=f"No results found for: {query}")]

            # Format results as markdown
            output_lines = [f'# Gnōsis Search Results: "{query}"\n']
            output_lines.append(f"Found {len(results)} results:\n")

            for i, r in enumerate(results, 1):
                output_lines.append(f"## [{i}] {r.get('title', 'Untitled')}")
                output_lines.append(f"- **Source**: {r.get('source', 'Unknown')}")
                output_lines.append(f"- **Citations**: {r.get('citations', 'N/A')}")
                output_lines.append(
                    f"- **Authors**: {r.get('authors', 'Unknown')[:100]}..."
                )
                output_lines.append(f"- **Abstract**: {r.get('abstract', '')[:300]}...")
                if r.get("url"):
                    output_lines.append(f"- **URL**: {r.get('url')}")
                output_lines.append("")

            log(f"Search completed: {len(results)} results")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Search error: {e}")
            return [TextContent(type="text", text=f"Error searching: {str(e)}")]

    elif name == "stats":
        try:
            with StdoutSuppressor():
                from mekhane.anamnesis.index import GnosisIndex

            log("Getting stats...")
            index = GnosisIndex()
            stats = index.get_stats()

            output_lines = ["# Gnōsis Knowledge Base Statistics\n"]
            output_lines.append(f"- **Total Papers**: {stats.get('total_papers', 0)}")
            output_lines.append(f"- **Sources**: {', '.join(stats.get('sources', []))}")
            output_lines.append(
                f"- **Last Updated**: {stats.get('last_updated', 'Never')}"
            )

            log("Stats completed")
            return [TextContent(type="text", text="\n".join(output_lines))]

        except Exception as e:
            log(f"Stats error: {e}")
            return [TextContent(type="text", text=f"Error getting stats: {str(e)}")]

    elif name == "recommend_model":
        task_desc = arguments.get("task_description", "").lower()

        if not task_desc:
            return [
                TextContent(type="text", text="Error: task_description is required")
            ]

        log(f"Recommending model for: {task_desc[:50]}...")

        # Priority rules based on model-selection-guide.md
        priority_rules = [
            (
                "P1",
                [
                    "セキュリティ",
                    "security",
                    "監査",
                    "audit",
                    "コンプライアンス",
                    "compliance",
                    "品質保証",
                    "quality",
                ],
                "Claude",
            ),
            (
                "P2",
                [
                    "画像",
                    "image",
                    "ui",
                    "ux",
                    "図",
                    "diagram",
                    "可視化",
                    "visualization",
                    "デザイン",
                    "design",
                ],
                "Gemini",
            ),
            (
                "P3",
                [
                    "探索",
                    "explore",
                    "ブレスト",
                    "brainstorm",
                    "プロトタイプ",
                    "prototype",
                    "mvp",
                    "試作",
                ],
                "Gemini",
            ),
            (
                "P4",
                ["高速", "fast", "バッチ", "batch", "初期調査", "triage", "トリアージ"],
                "Gemini Flash",
            ),
        ]

        detected_keywords = []
        matched_priority = None
        recommended_model = "Claude"  # Default P5

        for priority, keywords, model in priority_rules:
            for kw in keywords:
                if kw in task_desc:
                    detected_keywords.append(kw)
                    if matched_priority is None:
                        matched_priority = priority
                        recommended_model = model

        if matched_priority is None:
            matched_priority = "P5"

        output_lines = [
            "# [Hegemonikon] T2 Krisis (Model Selection)\n",
            f"- **Task**: {arguments.get('task_description', '')}",
            f"- **Detected Keywords**: {', '.join(detected_keywords) if detected_keywords else '(none)'}",
            f"- **Priority**: {matched_priority}",
            f"- **Recommended Model**: {recommended_model}",
            "",
            "## Reasoning",
        ]

        if matched_priority == "P1":
            output_lines.append(
                "Security/audit tasks require Claude's strict, deterministic reasoning."
            )
        elif matched_priority == "P2":
            output_lines.append(
                "Multimodal/visual tasks benefit from Gemini's image capabilities."
            )
        elif matched_priority == "P3":
            output_lines.append(
                "Exploratory tasks benefit from Gemini's creative, non-deterministic approach."
            )
        elif matched_priority == "P4":
            output_lines.append(
                "High-speed/batch tasks are optimized for Gemini Flash."
            )
        else:
            output_lines.append(
                "No specific task type detected. Default to Claude for precision and consistency."
            )

        log(f"Model recommendation: {recommended_model}")
        return [TextContent(type="text", text="\n".join(output_lines))]

    else:
# PURPOSE: Run the MCP server.
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# PURPOSE: gnosis_mcp_server の main 処理を実行する
async def main():
    """Run the MCP server."""
    log("Starting stdio server...")
    try:
        async with stdio_server() as streams:
            log("stdio_server connected")
            await server.run(
                streams[0],  # read_stream
                streams[1],  # write_stream
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
