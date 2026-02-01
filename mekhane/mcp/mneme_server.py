# PROOF: [L2/インフラ] A0→MCP経由のアクセスが必要→mneme_server が担う
#!/usr/bin/env python3
"""
Mneme MCP Server - Hegemonikón Symplokē Integration

Model Context Protocol server for integrated knowledge search across
Gnōsis, Chronos, Sophia, and Kairos indices.

CRITICAL: This file follows MCP stdio protocol rules:
- All debug/log output goes to STDERR
- STDOUT is reserved for MCP protocol JSON-RPC
"""

import sys
import io

# Prevent any accidental stdout pollution
_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr


def log(msg):
    """Debug logging to stderr."""
    print(f"[mneme] {msg}", file=sys.stderr)


log("Starting Mneme MCP Server...")
log(f"Python: {sys.executable}")
log(f"Platform: {sys.platform}")

# ============ Import path setup ============
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
log(f"Added to path: {Path(__file__).parent.parent}")


# ============ Suppress stdout during imports ============
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


# ============ Import MCP SDK ============
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent

    log("MCP imports successful")
except Exception as e:
    log(f"MCP import error: {e}")
    sys.exit(1)


# ============ Import Symplokē components ============
try:
    with StdoutSuppressor():
        from mekhane.symploke.search.engine import SearchEngine
        from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
        from mekhane.symploke.indices import (
            GnosisIndex,
            ChronosIndex,
            SophiaIndex,
            KairosIndex,
            Document,
        )
    log("Symplokē imports successful (EmbeddingAdapter mode)")
except Exception as e:
    log(f"Symplokē import error: {e}")
    # Continue without Symplokē - stub mode
    SearchEngine = None


# ============ Initialize MCP server ============
server = Server(
    name="mneme",
    version="1.0.0",
    instructions="Mneme: Hegemonikón integrated knowledge search across 4 sources",
)
log("Server initialized")


# ============ Initialize SearchEngine ============
_engine = None


def get_engine():
    """Lazy initialization of SearchEngine."""
    global _engine
    if _engine is None and SearchEngine is not None:
        log("Initializing SearchEngine...")
        _engine = SearchEngine()

        # Load seed data for MVP testing
        try:
            from mekhane.symploke.seed_data import (
                GNOSIS_SEED,
                CHRONOS_SEED,
                SOPHIA_SEED,
                KAIROS_SEED,
            )

            seed_data = {
                "gnosis": GNOSIS_SEED,
                "chronos": CHRONOS_SEED,
                "sophia": SOPHIA_SEED,
                "kairos": KAIROS_SEED,
            }
            log("Seed data loaded")
        except ImportError:
            seed_data = {}
            log("No seed data available")

        # Register all indices with EmbeddingAdapter (semantic search mode)
        # Using MiniLM-L6-v2: 384 dimensions
        embedding_adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
        log("EmbeddingAdapter initialized")

        for IndexClass, name in [
            (GnosisIndex, "gnosis"),
            (ChronosIndex, "chronos"),
            (SophiaIndex, "sophia"),
            (KairosIndex, "kairos"),
        ]:
            adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
            index = IndexClass(adapter, name, dimension=384)
            index.initialize()

            # Ingest seed data if available
            if name in seed_data:
                count = index.ingest(seed_data[name])
                log(f"Registered {name} index ({count} docs)")
            else:
                log(f"Registered {name} index (empty)")

            _engine.register(index)

        log("SearchEngine ready")
    return _engine


# ============ Tool definitions ============
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search",
            description="Search across Gnōsis, Chronos, Sophia, and Kairos indices",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: limit to specific sources (gnosis, chronos, sophia, kairos)",
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of results (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="stats",
            description="Get statistics about indexed documents",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="sources",
            description="List available knowledge sources",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    log(f"Tool call: {name} with args: {arguments}")

    try:
        if name == "search":
            return await _handle_search(arguments)
        elif name == "stats":
            return await _handle_stats(arguments)
        elif name == "sources":
            return await _handle_sources(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        log(f"Tool error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _handle_search(arguments: dict) -> list[TextContent]:
    """Handle search tool."""
    query = arguments.get("query", "")
    sources = arguments.get("sources")
    k = arguments.get("k", 10)

    engine = get_engine()
    if engine is None:
        return [TextContent(type="text", text="SearchEngine not available (stub mode)")]

    results = engine.search(query, sources=sources, k=k)

    if not results:
        return [TextContent(type="text", text=f"No results for: {query}")]

    # Format results
    lines = [f"## Search Results for: {query}", f"Found {len(results)} results\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. [{r.source.value}] {r.doc_id}")
        lines.append(f"Score: {r.score:.3f}")
        if r.content:
            lines.append(f"Content: {r.content[:200]}...")
        lines.append("")

    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_stats(arguments: dict) -> list[TextContent]:
    """Handle stats tool."""
    engine = get_engine()
    if engine is None:
        return [TextContent(type="text", text="SearchEngine not available (stub mode)")]

    stats = engine.stats()

    lines = ["## Mneme Statistics\n"]
    total = 0
    for source, count in stats.items():
        lines.append(f"- **{source}**: {count} documents")
        total += count
    lines.append(f"\n**Total**: {total} documents")

    return [TextContent(type="text", text="\n".join(lines))]


async def _handle_sources(arguments: dict) -> list[TextContent]:
    """Handle sources tool."""
    engine = get_engine()
    if engine is None:
        sources = ["gnosis", "chronos", "sophia", "kairos"]
    else:
        sources = list(engine.registered_sources)

    lines = ["## Available Knowledge Sources\n"]
    descriptions = {
        "gnosis": "External knowledge (research papers, documentation)",
        "chronos": "Chat history (time-ordered conversations)",
        "sophia": "Knowledge items (distilled insights)",
        "kairos": "Session handoffs (context continuity)",
    }

    for source in sources:
        desc = descriptions.get(source, "Unknown source")
        lines.append(f"- **{source}**: {desc}")

    return [TextContent(type="text", text="\n".join(lines))]


# ============ Main ============
async def main():
    """Run the MCP server."""
    log("Starting stdio server...")

    # Initialize engine
    get_engine()

    async with stdio_server() as (read, write):
        log("Stdio streams ready")
        await server.run(read, write, server.create_initialization_options())

    log("Server shutdown")


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
