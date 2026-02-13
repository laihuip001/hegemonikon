# PROOF: [L2/インフラ] <- mekhane/mcp/ A0→MCP経由のアクセスが必要→digestor_mcp_server が担う
#!/usr/bin/env python3
"""
Digestor MCP Server - Hegemonikón Knowledge Digestion Pipeline

Model Context Protocol server for automated knowledge ingestion.
Exposes digestor tools via stdio transport.

CRITICAL: This file follows MCP stdio protocol rules:
- NO print() to stdout (use stderr for debugging)
- All communication via MCP protocol only
"""

import sys
import io

_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr


# Debug logging to stderr (won't interfere with MCP stdio)
# PURPOSE: log — MCPサービスの処理
def log(msg):
    print(f"[Digestor MCP] {msg}", file=_stderr_wrapper)


log("Starting Digestor MCP Server...")

# ============ Import path setup ============
from pathlib import Path

# mekhane/mcp/ → mekhane/ → hegemonikon/ (project root)
_mekhane_dir = Path(__file__).parent.parent
_project_root = _mekhane_dir.parent

# Both paths needed: project root for `from mekhane.xxx` imports,
# mekhane dir for any relative imports within mekhane
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


# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent

    log("MCP imports successful")
except Exception as e:
    log(f"MCP import error: {e}")
    sys.exit(1)

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

# Initialize MCP server
server = Server(
    name="digestor",
    version="1.0.0",
    instructions="Digestor: Automated knowledge ingestion pipeline (Gnosis → /eat)",
)
log("Server initialized")
# PURPOSE: List available tools.


@server.list_tools()
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
    ]
# PURPOSE: tool calls の安全な処理を保証する


@server.call_tool()
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

# PURPOSE: トピック一覧取得
    return [TextContent(type="text", text=output)]


# PURPOSE: get topics を処理する
async def handle_get_topics(arguments: dict):
    """トピック一覧取得"""
    if DigestorSelector is None:
        return [TextContent(type="text", text="Digestor module not available")]

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


# PURPOSE: digestor_mcp_server の main 処理を実行する
async def main():
    """Run the MCP server."""
    log("Starting stdio server...")
    sys.stdout = _original_stdout

    async with stdio_server() as streams:
        log("Stdio streams acquired")
        await server.run(streams[0], streams[1], server.create_initialization_options())


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
