# PROOF: [L2/インフラ] <- mekhane/mcp/ A0→MCP経由のアクセスが必要→mneme_server が担う
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


# PURPOSE: Debug logging to stderr.
def log(msg):
    """Debug logging to stderr."""
    print(f"[mneme] {msg}", file=sys.stderr)


log("Starting Mneme MCP Server...")
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
        from mekhane.symploke.indices.gnosis_lance_bridge import GnosisLanceBridge
    log("Symplokē imports successful (EmbeddingAdapter + LanceBridge mode)")
except Exception as e:
    log(f"Symplokē import error: {e}")
    # Continue without Symplokē - stub mode
    SearchEngine = None
    GnosisLanceBridge = None


# ============ Initialize MCP server ============
server = Server(
    name="mneme",
    version="1.0.0",
    instructions="Mneme: Hegemonikón unified knowledge server (Gnōsis papers + Sophia KI + Kairos handoffs + Chronos chat)",
)
log("Server initialized")


# ============ Initialize SearchEngine ============
# PURPOSE: Lazy initialization of SearchEngine.
_engine = None


# PURPOSE: engine を取得する
def get_engine():
    """Lazy initialization of SearchEngine."""
    global _engine
    if _engine is None and SearchEngine is not None:
        log("Initializing SearchEngine...")
        _engine = SearchEngine()

        # --- Real index paths (built by kairos_ingest.py / sophia_ingest.py) ---
        _indices_dir = _project_root.parent / "mneme" / ".hegemonikon" / "indices"
        _real_indices = {
            "kairos": _indices_dir / "kairos.pkl",
            "sophia": _indices_dir / "sophia.pkl",
        }

        # --- Seed data fallback ---
        seed_data = {}
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
            log("Seed data loaded (fallback)")
        except ImportError:
            log("No seed data available")

        # --- Register gnosis: LanceBridge (27,432 papers) or seed fallback ---
        if GnosisLanceBridge is not None:
            try:
                bridge = GnosisLanceBridge()
                count = bridge.count()
                _engine.register(bridge)
                log(f"Loaded gnosis via LanceBridge ({count} docs)")
            except Exception as e:
                log(f"LanceBridge failed: {e}, falling back to seed")
                adapter = EmbeddingAdapter()
                index = GnosisIndex(adapter, "gnosis", dimension=384)
                index.initialize()
                if "gnosis" in seed_data:
                    index.ingest(seed_data["gnosis"])
                _engine.register(index)
        else:
            adapter = EmbeddingAdapter()
            index = GnosisIndex(adapter, "gnosis", dimension=384)
            index.initialize()
            if "gnosis" in seed_data:
                index.ingest(seed_data["gnosis"])
            _engine.register(index)
            log("Registered gnosis from seed")

        # --- Register chronos, sophia, kairos: .pkl first, seed fallback ---
        for IndexClass, name in [
            (ChronosIndex, "chronos"),
            (SophiaIndex, "sophia"),
            (KairosIndex, "kairos"),
        ]:
            pkl_path = _real_indices.get(name)

            if pkl_path and pkl_path.exists():
                adapter = EmbeddingAdapter()
                index = IndexClass(adapter, name, dimension=1024)
                index.load(str(pkl_path))
                count = index.count()
                log(f"Loaded {name} from {pkl_path.name} ({count} docs)")
            else:
                adapter = EmbeddingAdapter()
                index = IndexClass(adapter, name, dimension=384)
                index.initialize()
                if name in seed_data:
                    count = index.ingest(seed_data[name])
                    log(f"Registered {name} from seed ({count} docs)")
                else:
                    log(f"Registered {name} (empty)")

            _engine.register(index)

        log("SearchEngine ready")
    return _engine

# PURPOSE: List available tools.

# ============ Tool definitions ============
@server.list_tools()
# PURPOSE: [L2-auto] List available tools.
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
        # === From gnosis ===
        Tool(
            name="search_papers",
            description="Search the Gnōsis knowledge base for academic papers. Returns relevant papers with titles, authors, abstracts, and citations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (e.g., 'transformer attention mechanism')"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 5)", "default": 5},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="recommend_model",
            description="Recommend the best AI model (Claude/Gemini) for a given task based on T2 Krisis priority rules (P1-P5). Returns model recommendation with detected keywords and reasoning.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_description": {"type": "string", "description": "Description of the task to analyze (e.g., 'UI design for dashboard', 'security audit of API')"},
                },
                "required": ["task_description"],
            },
        ),
        # === From sophia ===
        Tool(
            name="backlinks",
            description="Get backlinks for a Knowledge Item. Shows which KIs reference the given one via [[wikilink]] syntax.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ki_name": {"type": "string", "description": "Name of the Knowledge Item to get backlinks for"},
                },
                "required": ["ki_name"],
            },
        ),
        Tool(
            name="graph_stats",
            description="Get knowledge graph statistics (nodes, edges, most linked items)",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]
# PURPOSE: tool calls の安全な処理を保証する


@server.call_tool()
# PURPOSE: [L2-auto] Handle tool calls.
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
        elif name == "search_papers":
            return await _handle_search_papers(arguments)
        elif name == "recommend_model":
            return await _handle_recommend_model(arguments)
        elif name == "backlinks":
            return await _handle_backlinks(arguments)
        elif name == "graph_stats":
            return await _handle_graph_stats(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        log(f"Tool error: {e}")
# PURPOSE: search tool の安全な処理を保証する
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# PURPOSE: [L2-auto] Handle search tool.
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

# PURPOSE: stats tool の安全な処理を保証する
    return [TextContent(type="text", text="\n".join(lines))]


# PURPOSE: [L2-auto] Handle stats tool.
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

# PURPOSE: sources tool の安全な処理を保証する
    return [TextContent(type="text", text="\n".join(lines))]


# PURPOSE: [L2-auto] Handle sources tool.
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


# ============ Gnosis tools (from gnosis_mcp_server.py) ============

# PURPOSE: [L2-auto] Handle search_papers tool.
async def _handle_search_papers(arguments: dict) -> list[TextContent]:
    """Search Gnosis papers via GnosisIndex (LanceDB)."""
    query = arguments.get("query", "")
    limit = arguments.get("limit", 5)
    if not query:
        return [TextContent(type="text", text="Error: query is required")]
    try:
        with StdoutSuppressor():
            from mekhane.anamnesis.index import GnosisIndex
            index = GnosisIndex()
            results = index.search(query, k=limit)
        if not results:
            return [TextContent(type="text", text=f"No results found for: {query}")]
        lines = [f'# Gnōsis Search Results: "{query}"\n', f"Found {len(results)} results:\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"## [{i}] {r.get('title', 'Untitled')}")
            lines.append(f"- **Source**: {r.get('source', 'Unknown')}")
            lines.append(f"- **Citations**: {r.get('citations', 'N/A')}")
            authors = r.get('authors', 'Unknown')
            if isinstance(authors, str):
                authors = authors[:100]
            lines.append(f"- **Authors**: {authors}")
            abstract = r.get('abstract', '')
            if isinstance(abstract, str):
                abstract = abstract[:300]
            lines.append(f"- **Abstract**: {abstract}...")
            if r.get("url"):
                lines.append(f"- **URL**: {r.get('url')}")
            lines.append("")
        log(f"search_papers completed: {len(results)} results")
        return [TextContent(type="text", text="\n".join(lines))]
    except Exception as e:
        log(f"search_papers error: {e}")
        return [TextContent(type="text", text=f"Error searching papers: {str(e)}")]


# PURPOSE: [L2-auto] Handle recommend_model tool.
async def _handle_recommend_model(arguments: dict) -> list[TextContent]:
    """Recommend AI model based on Krisis priority rules."""
    task_desc = arguments.get("task_description", "").lower()
    if not task_desc:
        return [TextContent(type="text", text="Error: task_description is required")]
    log(f"Recommending model for: {task_desc[:50]}...")
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
                if matched_priority is None:
                    matched_priority = priority
                    recommended_model = model
    if matched_priority is None:
        matched_priority = "P5"
    lines = [
        "# [Hegemonikon] T2 Krisis (Model Selection)\n",
        f"- **Task**: {arguments.get('task_description', '')}",
        f"- **Detected Keywords**: {', '.join(detected_keywords) if detected_keywords else '(none)'}",
        f"- **Priority**: {matched_priority}",
        f"- **Recommended Model**: {recommended_model}",
    ]
    return [TextContent(type="text", text="\n".join(lines))]


# ============ Sophia tools (from sophia_mcp_server.py) ============

_KI_DIR = Path("/home/makaron8426/.gemini/antigravity/knowledge")


# PURPOSE: [L2-auto] Handle backlinks tool.
async def _handle_backlinks(arguments: dict) -> list[TextContent]:
    """Get backlinks for a Knowledge Item."""
    ki_name = arguments.get("ki_name", "")
    if not ki_name:
        return [TextContent(type="text", text="Error: ki_name is required")]
    try:
        with StdoutSuppressor():
            from mekhane.symploke.sophia_backlinker import SophiaBacklinker
        log(f"Getting backlinks for: {ki_name}")
        backlinker = SophiaBacklinker()
        backlinker.build_graph()
        backlinks = backlinker.get_backlinks(ki_name)
        outlinks = backlinker.get_outlinks(ki_name)
        lines = [f"# Backlinks: {ki_name}\n"]
        if backlinks:
            lines.append(f"## ← Backlinks ({len(backlinks)})")
            for link in sorted(backlinks):
                lines.append(f"- {link}")
        else:
            lines.append("No backlinks found.")
        lines.append("")
        if outlinks:
            lines.append(f"## → Outlinks ({len(outlinks)})")
            for link in sorted(outlinks):
                lines.append(f"- {link}")
        return [TextContent(type="text", text="\n".join(lines))]
    except Exception as e:
        log(f"Backlinks error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# PURPOSE: [L2-auto] Handle graph_stats tool.
async def _handle_graph_stats(arguments: dict) -> list[TextContent]:
    """Get knowledge graph statistics."""
    try:
        with StdoutSuppressor():
            from mekhane.symploke.sophia_backlinker import SophiaBacklinker
        log("Getting graph stats...")
        backlinker = SophiaBacklinker()
        backlinker.build_graph()
        stats = backlinker.get_stats()
        lines = ["# Knowledge Graph Statistics\n"]
        lines.append(f"- **Nodes**: {stats['nodes']}")
        lines.append(f"- **Edges**: {stats['edges']}")
        lines.append(f"- **Isolated**: {stats['isolated']}")
        if stats["most_linked"]:
            lines.append("\n## Most Linked")
            for name, count in stats["most_linked"]:
                if count > 0:
                    lines.append(f"- **{name}**: {count} backlinks")
        return [TextContent(type="text", text="\n".join(lines))]
    except Exception as e:
        log(f"Graph stats error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# PURPOSE: Run the MCP server.


# ============ Main ============
# PURPOSE: [L2-auto] Run the MCP server.
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
