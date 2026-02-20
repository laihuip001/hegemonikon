# PROOF: [L2/インフラ] <- mekhane/mcp/ A0→MCP経由のアクセスが必要→digestor_mcp_server が担う
#!/usr/bin/env python3
"""
Digestor MCP Server v2.1 - Hegemonikón Knowledge Digestion Pipeline

Tools: list_candidates, run_digestor, get_topics, check_incoming,
       mark_processed, paper_search, paper_details, paper_citations
"""

import sys
from pathlib import Path
from mekhane.mcp.mcp_base import MCPBase, StdoutSuppressor

# Initialize via shared infrastructure
_base = MCPBase(
    name="digestor",
    version="2.1.0",
    instructions="Digestor: Knowledge ingestion pipeline (Gnosis → /eat) + Semantic Scholar API (paper search/details/citations)",
)
server = _base.server
log = _base.log
TextContent = _base.TextContent
Tool = _base.Tool

# Import Digestor modules
try:
    with StdoutSuppressor():
        from mekhane.ergasterion.digestor.selector import DigestorSelector
        from mekhane.ergasterion.digestor.pipeline import DigestorPipeline
    log("Digestor imports successful")
except Exception as e:
    log(f"Digestor import error: {e}")
    log("Will run with stub mode")
    DigestorSelector = None
    DigestorPipeline = None
# PURPOSE: List available tools.


@server.list_tools()
# PURPOSE: [L2-auto] List available tools.
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="list_candidates",
            description="消化候補をリストする。Gnosis から収集した論文を分析し、消化すべき候補を選定。",
            inputSchema={
                "type": "object",
                "properties": {
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "対象トピック（省略時は全トピック）",
                    },
                    "max_candidates": {
                        "type": "integer",
                        "default": 10,
                        "description": "最大候補数",
                    },
                },
            },
        ),
        Tool(
            name="run_digestor",
            description="消化パイプラインを実行。Gnosis → /eat 連携を自動化。",
            inputSchema={
                "type": "object",
                "properties": {
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "対象トピック",
                    },
                    "dry_run": {
                        "type": "boolean",
                        "default": True,
                        "description": "Dry run モード（レポート生成のみ）",
                    },
                    "max_papers": {
                        "type": "integer",
                        "default": 50,
                        "description": "取得する最大論文数",
                    },
                },
            },
        ),
        Tool(
            name="get_topics",
            description="消化対象トピック一覧を取得。",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="check_incoming",
            description="incoming/ の未消化ファイルを確認。消化待ちの論文候補一覧を返す。",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="mark_processed",
            description="消化完了したファイルを incoming/ → processed/ に移動。",
            inputSchema={
                "type": "object",
                "properties": {
                    "filenames": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "移動するファイル名のリスト。省略時は全 eat_*.md を移動",
                    },
                },
            },
        ),
        # === Semantic Scholar API (自作クライアント統合) ===
        Tool(
            name="paper_search",
            description="Search academic papers via Semantic Scholar API. Returns titles, authors, abstracts, citation counts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (e.g., 'free energy principle')"},
                    "limit": {"type": "integer", "default": 10, "description": "Max results (1-100)"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="paper_details",
            description="Get detailed info for a specific paper by Semantic Scholar ID, DOI, or arXiv ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "S2 Paper ID, DOI (e.g., '10.1038/s41586-021-03819-2'), or arXiv ID (e.g., 'arXiv:2106.01345')"},
                },
                "required": ["paper_id"],
            },
        ),
        Tool(
            name="paper_citations",
            description="Get papers that cite a given paper.",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "S2 Paper ID, DOI, or arXiv ID"},
                    "limit": {"type": "integer", "default": 10, "description": "Max citations to return"},
                },
                "required": ["paper_id"],
            },
        ),
    ]
# PURPOSE: tool calls の安全な処理を保証する


@server.call_tool()
# PURPOSE: [L2-auto] Handle tool calls.
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    log(f"Tool call: {name} with args: {arguments}")

    try:
        if name == "list_candidates":
            return await handle_list_candidates(arguments)
        elif name == "run_digestor":
            return await handle_run_digestor(arguments)
        elif name == "get_topics":
            return await handle_get_topics(arguments)
        elif name == "check_incoming":
            return await handle_check_incoming(arguments)
        elif name == "mark_processed":
            return await handle_mark_processed(arguments)
        elif name in ("paper_search", "paper_details", "paper_citations"):
            return await handle_semantic_scholar(name, arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        log(f"Tool error: {e}")
# PURPOSE: 消化候補をリスト
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# PURPOSE: list candidates を処理する
async def handle_list_candidates(arguments: dict):
    """消化候補をリスト"""
    if DigestorPipeline is None:
        return [TextContent(type="text", text="Digestor module not available")]

    topics = arguments.get("topics")
    max_candidates = arguments.get("max_candidates", 10)

    # pipeline.run() は print() で stdout に出力する → MCP stdio を汚染するため抑制
    with StdoutSuppressor():
        pipeline = DigestorPipeline()
        result = pipeline.run(topics=topics, max_candidates=max_candidates, dry_run=True)

    output = f"=== 消化候補リスト ===\n"
    output += f"総論文数: {result.total_papers}\n"
    output += f"選定候補: {result.candidates_selected}\n\n"

    for i, c in enumerate(result.candidates, 1):
        output += f"{i}. [{c.score:.2f}] {c.paper.title[:60]}...\n"
        output += f"   Topics: {', '.join(c.matched_topics)}\n"
        output += f"   Source: {c.paper.source}\n\n"

# PURPOSE: 消化パイプライン実行
    return [TextContent(type="text", text=output)]


# PURPOSE: run digestor を処理する
async def handle_run_digestor(arguments: dict):
    """消化パイプライン実行"""
    if DigestorPipeline is None:
        return [TextContent(type="text", text="Digestor module not available")]

    topics = arguments.get("topics")
    dry_run = arguments.get("dry_run", True)
    max_papers = arguments.get("max_papers", 50)

    # pipeline.run() は print() で stdout に出力する → MCP stdio を汚染するため抑制
    with StdoutSuppressor():
        pipeline = DigestorPipeline()
        result = pipeline.run(
            topics=topics,
            max_papers=max_papers,
            dry_run=dry_run,
        )

    output = f"=== Digestor パイプライン {'(Dry Run)' if dry_run else ''} ===\n"
    output += f"Timestamp: {result.timestamp}\n"
    output += f"Source: {result.source}\n"
    output += f"総論文数: {result.total_papers}\n"
    output += f"選定候補: {result.candidates_selected}\n\n"

    if result.candidates:
        output += "消化候補:\n"
        for i, c in enumerate(result.candidates, 1):
            output += f"  {i}. {c.paper.title[:50]}... (score: {c.score:.2f})\n"

    # F4: Falsification matching — check digested papers against epistemic_status.yaml
    try:
        from mekhane.dendron.falsification_matcher import check_falsification, format_alerts

        for c in (result.candidates or []):
            paper_text = f"{c.paper.title} {getattr(c.paper, 'abstract', '')}"
            alerts = check_falsification(paper_text, c.paper.title, threshold=0.4)
            if alerts:
                output += f"\n{format_alerts(alerts, c.paper.title)}\n"
    except Exception as e:
        log(f"Falsification check skipped: {e}")

# PURPOSE: トピック一覧取得
    return [TextContent(type="text", text=output)]


# PURPOSE: get topics を処理する
async def handle_get_topics(arguments: dict):
    """トピック一覧取得"""
    if DigestorSelector is None:
        return [TextContent(type="text", text="Digestor module not available")]

    # DigestorSelector の初期化でも stdout に出力される可能性があるため抑制
    with StdoutSuppressor():
        selector = DigestorSelector()
        topics = selector.get_topics()

    output = "=== 消化対象トピック ===\n\n"
    for t in topics:
        output += f"- **{t.get('id')}**: {t.get('description', '')}\n"
        output += f"  Query: {t.get('query', '')}\n"
        digest_to = t.get("digest_to", [])
        if digest_to:
            output += f"  消化先: {', '.join(digest_to)}\n"
        output += "\n"

# PURPOSE: Run the MCP server.
    return [TextContent(type="text", text=output)]


# PURPOSE: incoming/ の未消化ファイルを確認する
async def handle_check_incoming(arguments: dict):
    """incoming/ の未消化ファイルを確認"""
    incoming_dir = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "incoming"

    if not incoming_dir.exists():
        return [TextContent(type="text", text="incoming/ ディレクトリが見つかりません")]

    files = sorted(incoming_dir.glob("eat_*.md"))
    if not files:
        return [TextContent(type="text", text="消化待ちの候補はありません (0 件)")]

    output = f"=== 消化待ち候補: {len(files)} 件 ===\n\n"

    for i, f in enumerate(files, 1):
        # YAML frontmatter からメタデータを抽出
        try:
            content = f.read_text(encoding="utf-8")
            title = "(タイトル不明)"
            score = ""
            topics = ""

            in_frontmatter = False
            for line in content.split("\n"):
                if line.strip() == "---":
                    if in_frontmatter:
                        break
                    in_frontmatter = True
                    continue
                if in_frontmatter:
                    if line.startswith("title:"):
                        title = line.split(":", 1)[1].strip().strip('"\'')
                    elif line.startswith("score:"):
                        score = line.split(":", 1)[1].strip()
                    elif line.startswith("topics:"):
                        topics = line.split(":", 1)[1].strip()

            output += f"{i}. {title}\n"
            if score:
                output += f"   Score: {score}\n"
            if topics:
                output += f"   Topics: {topics}\n"
            output += f"   File: {f.name}\n\n"
        except Exception as e:
            output += f"{i}. {f.name} (読取エラー: {e})\n\n"

    return [TextContent(type="text", text=output)]


# PURPOSE: 消化完了ファイルを processed/ に移動する
async def handle_mark_processed(arguments: dict):
    """消化完了ファイルを incoming/ → processed/ に移動"""
    if DigestorPipeline is None:
        return [TextContent(type="text", text="Digestor module not available")]

    from mekhane.ergasterion.digestor.pipeline import mark_as_processed

    filenames = arguments.get("filenames")
    result = mark_as_processed(filenames=filenames)

    output = f"=== processed/ 移動結果 ===\n"
    output += f"移動成功: {result['count']} 件\n\n"

    for f in result["moved"]:
        output += f"  ✅ {f}\n"
    for e in result["errors"]:
        output += f"  ❌ {e['file']}: {e['error']}\n"

    return [TextContent(type="text", text=output)]


# === Semantic Scholar handlers ===

async def handle_semantic_scholar(name: str, arguments: dict):
    """Handle Semantic Scholar API tools."""
    try:
        with StdoutSuppressor():
            from mekhane.pks.semantic_scholar import SemanticScholarClient
            import os
            api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
            client = SemanticScholarClient(api_key=api_key)
    except Exception as e:
        return [TextContent(type="text", text=f"Error initializing S2 client: {e}")]

    if name == "paper_search":
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        if not query:
            return [TextContent(type="text", text="Error: query is required")]
        try:
            papers = client.search(query, limit=min(limit, 100))
            if not papers:
                return [TextContent(type="text", text=f"No results for: {query}")]
            lines = [f'# Semantic Scholar: "{query}"\n', f"Found {len(papers)} results:\n"]
            for i, p in enumerate(papers, 1):
                lines.append(f"## [{i}] {p.title}")
                lines.append(f"- **Year**: {p.year or 'N/A'}")
                lines.append(f"- **Citations**: {p.citation_count}")
                lines.append(f"- **Authors**: {', '.join(p.authors[:5])}")
                if p.abstract:
                    lines.append(f"- **Abstract**: {p.abstract[:300]}...")
                if p.url:
                    lines.append(f"- **URL**: {p.url}")
                if p.doi:
                    lines.append(f"- **DOI**: {p.doi}")
                lines.append("")
            return [TextContent(type="text", text="\n".join(lines))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    elif name == "paper_details":
        paper_id = arguments.get("paper_id", "")
        if not paper_id:
            return [TextContent(type="text", text="Error: paper_id is required")]
        try:
            paper = client.get_paper(paper_id)
            if not paper:
                return [TextContent(type="text", text=f"Paper not found: {paper_id}")]
            lines = [
                f"# {paper.title}\n",
                f"- **Year**: {paper.year or 'N/A'}",
                f"- **Citations**: {paper.citation_count}",
                f"- **Authors**: {', '.join(paper.authors)}",
                f"- **DOI**: {paper.doi or 'N/A'}",
                f"- **arXiv**: {paper.arxiv_id or 'N/A'}",
                f"- **URL**: {paper.url or 'N/A'}",
            ]
            if paper.abstract:
                lines.append(f"\n## Abstract\n\n{paper.abstract}")
            return [TextContent(type="text", text="\n".join(lines))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    elif name == "paper_citations":
        paper_id = arguments.get("paper_id", "")
        limit = arguments.get("limit", 10)
        if not paper_id:
            return [TextContent(type="text", text="Error: paper_id is required")]
        try:
            citations = client.get_citations(paper_id, limit=limit)
            if not citations:
                return [TextContent(type="text", text=f"No citations found for: {paper_id}")]
            lines = [f"# Citations for {paper_id}\n", f"Found {len(citations)} citing papers:\n"]
            for i, p in enumerate(citations, 1):
                lines.append(f"{i}. **{p.title}** ({p.year or '?'}) — {p.citation_count} citations")
            return [TextContent(type="text", text="\n".join(lines))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    return [TextContent(type="text", text=f"Unknown S2 tool: {name}")]


if __name__ == "__main__":
    from mekhane.mcp.mcp_guard import guard
    guard("digestor")
    _base.run()
