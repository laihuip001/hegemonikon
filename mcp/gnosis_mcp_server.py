#!/usr/bin/env python3
"""
Gnōsis MCP Server

Model Context Protocol server for Hegemonikón knowledge base.
Exposes Gnōsis search and stats as MCP tools.

Usage:
    python gnosis_mcp_server.py

Register in Antigravity:
    1. Open Antigravity IDE
    2. Agent Panel → ... menu → MCP Servers → Manage
    3. Add custom server with command:
       python M:/Hegemonikon/mcp/gnosis_mcp_server.py
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize MCP server with required parameters
server = Server(
    name="gnosis",
    version="1.0.0",
    instructions="Gnōsis knowledge base for academic paper search"
)


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="search",
            description="Search the Gnōsis knowledge base for academic papers. Returns relevant papers with titles, authors, abstracts, and citations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'transformer attention mechanism')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="stats",
            description="Get statistics about the Gnōsis knowledge base (total papers, sources, etc.)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool(validate_input=True)
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    
    # Lazy import to avoid startup delay
    from mekhane.anamnesis.index import GnosisIndex
    
    if name == "search":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 5)
        
        if not query:
            return [TextContent(type="text", text="Error: query is required")]
        
        try:
            index = GnosisIndex()
            results = index.search(query, k=limit)
            
            if not results:
                return [TextContent(type="text", text=f"No results found for: {query}")]
            
            # Format results as markdown
            output_lines = [f"# Gnōsis Search Results: \"{query}\"\n"]
            output_lines.append(f"Found {len(results)} results:\n")
            
            for i, r in enumerate(results, 1):
                output_lines.append(f"## [{i}] {r.get('title', 'Untitled')}")
                output_lines.append(f"- **Source**: {r.get('source', 'Unknown')}")
                output_lines.append(f"- **Citations**: {r.get('citations', 'N/A')}")
                output_lines.append(f"- **Authors**: {r.get('authors', 'Unknown')[:100]}...")
                output_lines.append(f"- **Abstract**: {r.get('abstract', '')[:300]}...")
                if r.get('url'):
                    output_lines.append(f"- **URL**: {r.get('url')}")
                output_lines.append("")
            
            return [TextContent(type="text", text="\n".join(output_lines))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error searching: {str(e)}")]
    
    elif name == "stats":
        try:
            index = GnosisIndex()
            stats = index.get_stats()
            
            output_lines = ["# Gnōsis Knowledge Base Statistics\n"]
            output_lines.append(f"- **Total Papers**: {stats.get('total_papers', 0)}")
            output_lines.append(f"- **Sources**: {', '.join(stats.get('sources', []))}")
            output_lines.append(f"- **Last Updated**: {stats.get('last_updated', 'Never')}")
            
            return [TextContent(type="text", text="\n".join(output_lines))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting stats: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as streams:
        await server.run(
            streams[0],  # read_stream
            streams[1],  # write_stream
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
