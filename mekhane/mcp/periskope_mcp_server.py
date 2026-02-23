# PROOF: [L2/インフラ] <- mekhane/mcp/ Periskopē Deep Research を MCP ツールとして公開
# PURPOSE: Periskopē MCP Server v1.0 — Deep Research Engine via MCP
#!/usr/bin/env python3
"""
Periskopē MCP Server v1.0 — Deep Research Engine via MCP

Tools:
  - periskope_research: Full deep research pipeline (search + synthesis + verification)
  - periskope_search: Multi-source parallel search only (lightweight)
  - periskope_sources: Recommend optimal sources for a query
"""

import sys
from pathlib import Path
from mekhane.mcp.mcp_base import MCPBase, StdoutSuppressor

# Initialize via shared infrastructure
_base = MCPBase(
    name="periskope",
    version="1.0.0",
    instructions=(
        "Periskopē: Deep Research Engine. "
        "Multi-source search (SearXNG, Brave, Tavily, Semantic Scholar, Gnosis, Sophia, Kairos) "
        "+ multi-model synthesis (Gemini/Claude) + citation verification (BC-6 TAINT). "
        "Use periskope_search for quick searches, periskope_research for full deep research."
    ),
)
server = _base.server
log = _base.log
TextContent = _base.TextContent
Tool = _base.Tool

# Import Periskopē modules
PeriskopeEngine = None
try:
    with StdoutSuppressor():
        from mekhane.periskope.engine import PeriskopeEngine as _PE
    PeriskopeEngine = _PE
    log("Periskopē engine import successful")
except Exception as e:
    log(f"Periskopē import error: {e}")
    log("Will run with stub mode")


# PURPOSE: List available tools
@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="periskope_research",
            description=(
                "フル Deep Research パイプラインを実行。"
                "多ソース並列検索 → 多モデル合成 → 引用検証 → レポート生成。"
                "2-4分かかる場合がある (Deep Research は本来時間がかかるもの)。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "調査クエリ (例: 'Free Energy Principle と active inference の関係')",
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "使用するソース (省略=全ソース)。"
                            "選択肢: searxng, brave, tavily, semantic_scholar, gnosis, sophia, kairos"
                        ),
                    },
                    "depth": {
                        "type": "integer",
                        "default": 2,
                        "description": "調査深度。1=L1 Quick, 2=L2 Standard, 3=L3 Deep",
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 10,
                        "description": "ソースあたり最大結果数",
                    },
                    "auto_digest": {
                        "type": "boolean",
                        "default": False,
                        "description": "True で /eat incoming に自動書き出し",
                    },
                    "multipass": {
                        "type": "boolean",
                        "default": False,
                        "description": "True で W6 2パスリファインメント検索",
                    },
                    "expand_query": {
                        "type": "boolean",
                        "default": True,
                        "description": "True で W3 バイリンガルクエリ展開",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="periskope_search",
            description=(
                "多ソース並列検索のみ実行 (合成・引用検証なし)。"
                "軽量で高速 (10-15秒)。検索結果一覧を返す。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "検索クエリ",
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "使用するソース (省略=全ソース)",
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 10,
                        "description": "ソースあたり最大結果数",
                    },
                    "expand_query": {
                        "type": "boolean",
                        "default": True,
                        "description": "W3 バイリンガルクエリ展開",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="periskope_sources",
            description=(
                "クエリに最適な検索ソースを推薦する (F12 分類)。"
                "academic/implementation/news/concept に分類し、推奨ソースを返す。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "分類対象のクエリ",
                    },
                },
                "required": ["query"],
            },
        ),
    ]


# PURPOSE: Handle tool calls
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    log(f"Tool call: {name} with args: {arguments}")

    try:
        if name == "periskope_research":
            return await handle_research(arguments)
        elif name == "periskope_search":
            return await handle_search(arguments)
        elif name == "periskope_sources":
            return await handle_sources(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        log(f"Tool error: {e}")
        import traceback
        log(traceback.format_exc())
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# PURPOSE: Full deep research pipeline
async def handle_research(arguments: dict):
    """Full deep research pipeline."""
    if PeriskopeEngine is None:
        return [TextContent(type="text", text="Periskopē engine not available")]

    query = arguments.get("query", "")
    if not query:
        return [TextContent(type="text", text="Error: query is required")]

    sources = arguments.get("sources")
    depth = arguments.get("depth", 2)
    max_results = arguments.get("max_results", 10)
    auto_digest = arguments.get("auto_digest", False)
    multipass = arguments.get("multipass", False)
    expand_query = arguments.get("expand_query", True)

    log(f"Research: query={query!r}, depth=L{depth}, sources={sources}")

    with StdoutSuppressor():
        engine = PeriskopeEngine(
            max_results_per_source=max_results,
            verify_citations=True,
        )
        report = await engine.research(
            query=query,
            sources=sources,
            depth=depth,
            auto_digest=auto_digest,
            multipass=multipass,
            expand_query=expand_query,
        )

    md = report.markdown()
    log(
        f"Research complete: {len(report.search_results)} results, "
        f"{len(report.synthesis)} models, {report.elapsed_seconds:.1f}s"
    )
    return [TextContent(type="text", text=md)]


# PURPOSE: Search only (no synthesis/verification)
async def handle_search(arguments: dict):
    """Search only (no synthesis/verification)."""
    if PeriskopeEngine is None:
        return [TextContent(type="text", text="Periskopē engine not available")]

    query = arguments.get("query", "")
    if not query:
        return [TextContent(type="text", text="Error: query is required")]

    sources = arguments.get("sources")
    max_results = arguments.get("max_results", 10)
    expand_query = arguments.get("expand_query", True)

    log(f"Search: query={query!r}, sources={sources}")

    with StdoutSuppressor():
        engine = PeriskopeEngine(
            max_results_per_source=max_results,
            verify_citations=False,  # Search only — skip verification
        )
        report = await engine.research(
            query=query,
            sources=sources,
            depth=1,  # L1 — search only, Gemini Flash synthesis
            expand_query=expand_query,
        )

    # Format search results without full synthesis
    lines = [
        f"# Periskopē Search Results",
        f"",
        f"> **Query**: {query}",
        f"> **Time**: {report.elapsed_seconds:.1f}s",
        f"> **Results**: {len(report.search_results)} from {len(report.source_counts)} sources",
        f"",
    ]

    # Source breakdown
    lines.append("## Sources")
    lines.append("")
    lines.append("| Engine | Results |")
    lines.append("|:-------|--------:|")
    for source, count in sorted(report.source_counts.items()):
        lines.append(f"| {source} | {count} |")
    lines.append("")

    # Top results
    lines.append("## Results")
    lines.append("")
    for i, r in enumerate(report.search_results[:30], 1):
        lines.append(f"### [{i}] {r.title}")
        if r.url:
            lines.append(f"- **URL**: {r.url}")
        lines.append(f"- **Source**: {r.source.value}")
        lines.append(f"- **Relevance**: {r.relevance:.2f}")
        snippet = r.snippet or (r.content[:200] if r.content else "")
        if snippet:
            lines.append(f"- **Snippet**: {snippet}")
        lines.append("")

    # Include synthesis if available (L1 = Gemini Flash only)
    if report.synthesis:
        lines.append("## Quick Synthesis")
        lines.append("")
        for s in report.synthesis:
            lines.append(f"### {s.model.value} (Confidence: {s.confidence:.0%})")
            lines.append("")
            lines.append(s.content)
            lines.append("")

    log(f"Search complete: {len(report.search_results)} results, {report.elapsed_seconds:.1f}s")
    return [TextContent(type="text", text="\n".join(lines))]


# PURPOSE: Recommend optimal sources for a query
async def handle_sources(arguments: dict):
    """Recommend optimal sources for a query."""
    if PeriskopeEngine is None:
        return [TextContent(type="text", text="Periskopē engine not available")]

    query = arguments.get("query", "")
    if not query:
        return [TextContent(type="text", text="Error: query is required")]

    # F12: Query classification and source recommendation
    qtype = PeriskopeEngine._classify_query(query)
    recommended = PeriskopeEngine.select_sources(query)

    all_sources = {
        "searxng": "SearXNG (メタ検索エンジン — Google, Brave, DuckDuckGo 等を集約)",
        "brave": "Brave Search (プライバシー重視、2,000回/月無料)",
        "tavily": "Tavily (AI向け検索API、1,000回/月無料)",
        "semantic_scholar": "Semantic Scholar (学術論文、無制限)",
        "gnosis": "Gnōsis (HGK 内部知識ベース)",
        "sophia": "Sophia (HGK Sophia 知識)",
        "kairos": "Kairos (HGK 文脈知識)",
    }

    lines = [
        f"# Periskopē Source Recommendation",
        f"",
        f"> **Query**: {query}",
        f"> **Classification**: {qtype}",
        f"",
        f"## Recommended Sources",
        f"",
    ]
    for s in recommended:
        desc = all_sources.get(s, s)
        lines.append(f"- ✅ **{s}**: {desc}")
    lines.append("")

    lines.append("## All Available Sources")
    lines.append("")
    for s, desc in all_sources.items():
        marker = "✅" if s in recommended else "⬜"
        lines.append(f"- {marker} **{s}**: {desc}")

    return [TextContent(type="text", text="\n".join(lines))]


if __name__ == "__main__":
    _base.run()
