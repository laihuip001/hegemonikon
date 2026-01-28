#!/usr/bin/env python3
"""
Sophia MCP Server - Hegemonikón Knowledge Items Search

Model Context Protocol server for searching Sophia (KI) and Kairos (Handoff).
Exposes search tools via stdio transport.

CRITICAL: This file follows MCP stdio protocol rules:
- stdout: JSON-RPC messages ONLY
- stderr: All logging and debug output
"""

import sys
import os

# Platform-specific asyncio setup
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import io
_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr

def log(msg):
    print(f"[sophia-mcp] {msg}", file=sys.stderr, flush=True)

log("Starting Sophia MCP Server...")
log(f"Python: {sys.executable}")

# Import path setup
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
log(f"Added to path: {Path(__file__).parent.parent}")

# Suppress stdout during imports
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
    name="sophia",
    version="1.0.0",
    instructions="Sophia knowledge search for KIs and Handoffs"
)
log("Server initialized")


# Index paths
SOPHIA_INDEX = Path("/home/laihuip001/oikos/mneme/.hegemonikon/indices/sophia.pkl")
KAIROS_INDEX = Path("/home/laihuip001/oikos/mneme/.hegemonikon/indices/kairos.pkl")


@server.list_tools()
async def list_tools():
    """List available tools."""
    log("list_tools called")
    return [
        Tool(
            name="search",
            description="Search Sophia (Knowledge Items) and Kairos (Handoffs). Returns relevant knowledge with scores.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "source": {
                        "type": "string",
                        "description": "Source to search: 'sophia', 'kairos', or 'both' (default)",
                        "enum": ["sophia", "kairos", "both"],
                        "default": "both"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results per source (default: 5)",
                        "default": 5
                    },
                    "recent_days": {
                        "type": "integer",
                        "description": "Filter Kairos results to recent N days (optional)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="stats",
            description="Get statistics about Sophia and Kairos indices",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool(validate_input=True)
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    log(f"call_tool: {name} with {arguments}")
    
    if name == "search":
        query = arguments.get("query", "")
        source = arguments.get("source", "both")
        limit = arguments.get("limit", 5)
        recent_days = arguments.get("recent_days")
        
        if not query:
            return [TextContent(type="text", text="Error: query is required")]
        
        try:
            with StdoutSuppressor():
                from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
            
            log(f"Searching for: {query}")
            results = []
            
            # Search Sophia
            if source in ("sophia", "both") and SOPHIA_INDEX.exists():
                adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
                adapter.load(str(SOPHIA_INDEX))
                query_vec = adapter.encode([query])[0]
                sophia_results = adapter.search(query_vec, k=limit)
                
                for r in sophia_results:
                    results.append({
                        "source": "sophia",
                        "score": r.score,
                        "ki_name": r.metadata.get("ki_name", "N/A"),
                        "artifact": r.metadata.get("artifact", ""),
                        "summary": r.metadata.get("summary", "")[:150],
                        "file_path": r.metadata.get("file_path", "")
                    })
            
            # Search Kairos
            if source in ("kairos", "both") and KAIROS_INDEX.exists():
                adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
                adapter.load(str(KAIROS_INDEX))
                query_vec = adapter.encode([query])[0]
                kairos_results = adapter.search(query_vec, k=limit)
                
                from datetime import datetime, timedelta
                now = datetime.now()
                
                for r in kairos_results:
                    # Time filter
                    if recent_days:
                        ts = r.metadata.get("timestamp", "")
                        if ts:
                            try:
                                doc_date = datetime.fromisoformat(ts.split("T")[0])
                                if (now - doc_date).days > recent_days:
                                    continue
                            except:
                                pass
                    
                    results.append({
                        "source": "kairos",
                        "score": r.score,
                        "task": r.metadata.get("primary_task", "N/A"),
                        "timestamp": r.metadata.get("timestamp", ""),
                        "file_path": r.metadata.get("file_path", "")
                    })
            
            # Sort by score
            results.sort(key=lambda x: x["score"], reverse=True)
            results = results[:limit * 2]
            
            if not results:
                return [TextContent(type="text", text=f"No results found for: {query}")]
            
            # Format output
            output_lines = [f"# Sophia Search: \"{query}\"\n"]
            output_lines.append(f"Found {len(results)} results:\n")
            
            for i, r in enumerate(results, 1):
                if r["source"] == "sophia":
                    output_lines.append(f"## [{i}] [Sophia] {r['ki_name']}")
                    output_lines.append(f"- **Artifact**: {r['artifact']}")
                    output_lines.append(f"- **Summary**: {r['summary']}...")
                    output_lines.append(f"- **Score**: {r['score']:.3f}")
                else:
                    output_lines.append(f"## [{i}] [Kairos] {r['task']}")
                    output_lines.append(f"- **Timestamp**: {r['timestamp']}")
                    output_lines.append(f"- **Score**: {r['score']:.3f}")
                output_lines.append("")
            
            log(f"Search completed: {len(results)} results")
            return [TextContent(type="text", text="\n".join(output_lines))]
            
        except Exception as e:
            log(f"Search error: {e}")
            return [TextContent(type="text", text=f"Error searching: {str(e)}")]
    
    elif name == "stats":
        try:
            with StdoutSuppressor():
                from mekhane.symploke.adapters.embedding_adapter import EmbeddingAdapter
            
            log("Getting stats...")
            stats = {}
            
            if SOPHIA_INDEX.exists():
                adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
                adapter.load(str(SOPHIA_INDEX))
                stats["sophia_count"] = adapter.count()
            else:
                stats["sophia_count"] = 0
            
            if KAIROS_INDEX.exists():
                adapter = EmbeddingAdapter(model_name="all-MiniLM-L6-v2")
                adapter.load(str(KAIROS_INDEX))
                stats["kairos_count"] = adapter.count()
            else:
                stats["kairos_count"] = 0
            
            output_lines = ["# Sophia/Kairos Statistics\n"]
            output_lines.append(f"- **Sophia (Knowledge Items)**: {stats['sophia_count']} documents")
            output_lines.append(f"- **Kairos (Handoffs)**: {stats['kairos_count']} documents")
            output_lines.append(f"- **Total**: {stats['sophia_count'] + stats['kairos_count']} documents")
            
            log("Stats completed")
            return [TextContent(type="text", text="\n".join(output_lines))]
            
        except Exception as e:
            log(f"Stats error: {e}")
            return [TextContent(type="text", text=f"Error getting stats: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    log("Starting stdio server...")
    try:
        async with stdio_server() as streams:
            log("stdio_server connected")
            await server.run(
                streams[0],
                streams[1],
                server.create_initialization_options()
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
