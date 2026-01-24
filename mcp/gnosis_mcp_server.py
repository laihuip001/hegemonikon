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

# Debug logging to stderr (won't interfere with MCP stdio)
def log(msg):
    print(f"[gnosis-mcp] {msg}", file=sys.stderr, flush=True)

log("Starting Gnōsis MCP Server...")
log(f"Python: {sys.executable}")
log(f"CWD: {Path.cwd()}")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
log(f"Added to path: {Path(__file__).parent.parent}")

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    log("MCP imports successful")
except Exception as e:
    log(f"MCP import error: {e}")
    sys.exit(1)

# Initialize MCP server with required parameters
server = Server(
    name="gnosis",
    version="1.0.0",
    instructions="Gnōsis knowledge base for academic paper search"
)
log("Server initialized")



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
        ),
        Tool(
            name="recommend_model",
            description="Recommend the best AI model (Claude/Gemini) for a given task based on T2 Krisis priority rules (P1-P5). Returns model recommendation with detected keywords and reasoning.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Description of the task to analyze (e.g., 'UI design for dashboard', 'security audit of API')"
                    }
                },
                "required": ["task_description"]
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
    
    elif name == "recommend_model":
        task_desc = arguments.get("task_description", "").lower()
        
        if not task_desc:
            return [TextContent(type="text", text="Error: task_description is required")]
        
        # Priority rules based on model-selection-guide.md
        priority_rules = [
            ("P1", ["セキュリティ", "security", "監査", "audit", "コンプライアンス", "compliance", "品質保証", "quality"], "Claude"),
            ("P2", ["画像", "image", "ui", "ux", "図", "diagram", "可視化", "visualization", "デザイン", "design"], "Gemini"),
            ("P3", ["探索", "explore", "ブレスト", "brainstorm", "プロトタイプ", "prototype", "mvp", "試作"], "Gemini"),
            ("P4", ["高速", "fast", "バッチ", "batch", "初期調査", "triage", "トリアージ"], "Gemini Flash"),
        ]
        
        detected_keywords = []
        matched_priority = None
        recommended_model = "Claude"  # Default P5
        
        for priority, keywords, model in priority_rules:
            for kw in keywords:
                if kw in task_desc:
                    detected_keywords.append(kw)
                    if matched_priority is None:  # First match wins (higher priority)
                        matched_priority = priority
                        recommended_model = model
        
        if matched_priority is None:
            matched_priority = "P5"
        
        # Generate output in T2 Krisis format
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
            output_lines.append("Security/audit tasks require Claude's strict, deterministic reasoning.")
        elif matched_priority == "P2":
            output_lines.append("Multimodal/visual tasks benefit from Gemini's image capabilities.")
        elif matched_priority == "P3":
            output_lines.append("Exploratory tasks benefit from Gemini's creative, non-deterministic approach.")
        elif matched_priority == "P4":
            output_lines.append("High-speed/batch tasks are optimized for Gemini Flash.")
        else:
            output_lines.append("No specific task type detected. Default to Claude for precision and consistency.")
        
        return [TextContent(type="text", text="\n".join(output_lines))]
    
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
