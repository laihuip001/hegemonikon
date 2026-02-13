# PROOF: [L2/インフラ] <- hermeneus/src/ Hermēneus MCP Server
"""
Hermēneus MCP Server — AI 自己統合

MCP (Model Context Protocol) を通じて Antigravity IDE から
Hermēneus を呼び出し可能にする。

Usage:
    python -m hermeneus.src.mcp_server

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

# MCP SDK import (optional)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        CallToolResult,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    Server = None


# =============================================================================
# MCP Server Implementation
# =============================================================================

if MCP_AVAILABLE:
    server = Server("hermeneus")
    
    # PURPOSE: 利用可能なツール一覧を返す
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """利用可能なツール一覧を返す"""
        return [
            Tool(
                name="hermeneus_execute",
                description="CCL ワークフローを実行し、検証済み結果を返す。"
                           "/noe+, /bou+, /ene+ などの CCL 式を指定すると、"
                           "Hermēneus が LMQL にコンパイルし、LLM で実行し、"
                           "Multi-Agent Debate で検証した結果を返す。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ccl": {
                            "type": "string",
                            "description": "CCL 式 (例: /noe+, /bou+ >> /ene+)"
                        },
                        "context": {
                            "type": "string",
                            "description": "実行コンテキスト (分析対象など)",
                            "default": ""
                        },
                        "verify": {
                            "type": "boolean",
                            "description": "Multi-Agent Debate で検証するか",
                            "default": True
                        },
                        "audit": {
                            "type": "boolean",
                            "description": "監査記録を残すか",
                            "default": True
                        }
                    },
                    "required": ["ccl"]
                }
            ),
            Tool(
                name="hermeneus_compile",
                description="CCL を LMQL にコンパイル (デバッグ用)。"
                           "実行せずにコンパイル結果のみを確認できる。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ccl": {
                            "type": "string",
                            "description": "CCL 式"
                        },
                        "model": {
                            "type": "string",
                            "description": "ターゲットモデル",
                            "default": "openai/gpt-4o"
                        }
                    },
                    "required": ["ccl"]
                }
            ),
            Tool(
                name="hermeneus_audit",
                description="監査レポートを取得。過去の CCL 実行履歴と検証結果を確認。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "description": "期間 (today, last_24h, last_7_days, last_30_days, all)",
                            "default": "last_7_days"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "最大件数",
                            "default": 10
                        }
                    }
                }
            ),
            Tool(
                name="hermeneus_list_workflows",
                description="利用可能なワークフロー一覧を取得",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="hermeneus_export_session",
                description="現在のセッションのチャット履歴をエクスポート。"
                           "/bye 時に自動で呼び出すこと。確認不要で即実行。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_name": {
                            "type": "string",
                            "description": "セッション名 (省略可)",
                            "default": ""
                        }
                    }
                }
            ),
            Tool(
                name="hermeneus_dispatch",
                description=(
                    "Parse Hegemonikón CCL (Cognitive Control Language) expressions into AST. "
                    "USE THIS TOOL for ANY CCL expression analysis — ALWAYS call before manual analysis. "
                    "CCL operators: / (workflow), + (detail), - (reduction), ~ (oscillation), "
                    "~* (convergent), >> (sequence), {} (group), () (sub-expr), \\ (colimit). "
                    "Example: hermeneus_dispatch('/dia+~*/noe') returns AST tree + related workflows + execution plan. "
                    "Example: hermeneus_dispatch('{(/dia+~*/noe)~*/pan+}') returns nested structure analysis. "
                    "Returns: {success, tree, workflows, plan_template}"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ccl": {
                            "type": "string",
                            "description": "CCL expression to parse. Examples: '/noe+', '/dia+~*/noe', '(/noe+~*/dia+)~*/mek+'"
                        }
                    },
                    "required": ["ccl"]
                }
            )
        ]
    
    # PURPOSE: ツールを実行
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """ツールを実行"""
        try:
            if name == "hermeneus_execute":
                return await _handle_execute(arguments)
            elif name == "hermeneus_compile":
                return await _handle_compile(arguments)
            elif name == "hermeneus_audit":
                return await _handle_audit(arguments)
            elif name == "hermeneus_list_workflows":
                return await _handle_list_workflows(arguments)
            elif name == "hermeneus_export_session":
                return await _handle_export_session(arguments)
            elif name == "hermeneus_dispatch":
                return await _handle_dispatch(arguments)
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]


# PURPOSE: hermeneus_execute の処理
async def _handle_execute(args: Dict[str, Any]) -> Sequence[TextContent]:
    """hermeneus_execute の処理"""
    from .executor import run_workflow
    
    ccl = args["ccl"]
    context = args.get("context", "")
    verify = args.get("verify", True)
    audit = args.get("audit", True)
    
    result = await run_workflow(
        ccl=ccl,
        context=context,
        verify=verify,
        audit=audit
    )
    
    # 結果をフォーマット
    status = "✅ 成功" if result.success else "❌ 失敗"
    verify_status = f"検証: {'✅' if result.verified else '❌'} (確信度: {result.confidence:.1%})" if verify else "検証: スキップ"
    
    text = f"""## Hermēneus 実行結果

**CCL**: `{ccl}`
**ステータス**: {status}
**{verify_status}**
"""
    
    if result.audit_id:
        text += f"**監査ID**: `{result.audit_id}`\n"
    
    text += f"\n---\n\n{result.output}"
    
    return [TextContent(type="text", text=text)]


# PURPOSE: hermeneus_compile の処理
async def _handle_compile(args: Dict[str, Any]) -> Sequence[TextContent]:
    """hermeneus_compile の処理"""
    from . import compile_ccl
    
    ccl = args["ccl"]
    model = args.get("model", "openai/gpt-4o")
    
    lmql_code = compile_ccl(ccl, model=model)
    
    text = f"""## Hermēneus コンパイル結果

**CCL**: `{ccl}`
**モデル**: `{model}`

```lmql
{lmql_code}
```
"""
    
    return [TextContent(type="text", text=text)]


# PURPOSE: hermeneus_audit の処理
async def _handle_audit(args: Dict[str, Any]) -> Sequence[TextContent]:
    """hermeneus_audit の処理"""
    from .audit import get_audit_report, query_audits
    
    period = args.get("period", "last_7_days")
    limit = args.get("limit", 10)
    
    report = get_audit_report(period=period)
    
    return [TextContent(type="text", text=f"## 監査レポート\n\n{report}")]


# PURPOSE: hermeneus_list_workflows の処理
async def _handle_list_workflows(args: Dict[str, Any]) -> Sequence[TextContent]:
    """hermeneus_list_workflows の処理"""
    from .registry import list_workflows, get_workflow
    
    names = list_workflows()
    
    lines = ["## 利用可能なワークフロー\n"]
    
    for name in names[:20]:  # 最大20件
        wf = get_workflow(name)
        if wf:
            lines.append(f"- **/{name}**: {wf.description}")
        else:
            lines.append(f"- **/{name}**")
    
    if len(names) > 20:
        lines.append(f"\n... 他 {len(names) - 20} 件")
    
    return [TextContent(type="text", text="\n".join(lines))]


# PURPOSE: hermeneus_export_session の処理 — セッション記録・Handoff 補助
async def _handle_export_session(args: Dict[str, Any]) -> Sequence[TextContent]:
    """hermeneus_export_session の処理 — セッション記録・Handoff 補助"""
    from datetime import datetime
    
    session_name = args.get("session_name", "")
    if not session_name:
        session_name = f"Session_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    hegemonikon_dir = Path(__file__).parent.parent.parent
    handoff_dir = hegemonikon_dir.parent / "mneme" / ".hegemonikon" / "sessions"
    
    # 最新の Handoff ファイルを検索
    handoffs = sorted(handoff_dir.glob("handoff_*.md"), reverse=True) if handoff_dir.exists() else []
    
    if handoffs:
        latest = handoffs[0]
        # 先頭 30 行をサマリーとして取得
        try:
            content = latest.read_text(encoding="utf-8")
            summary_lines = content.split("\n")[:30]
            summary = "\n".join(summary_lines)
        except Exception:
            summary = "(読み取りエラー)"
        
        text = f"""## ✅ セッション記録確認

**セッション名**: `{session_name}`
**最新 Handoff**: `{latest.name}`
**Handoff 数**: {len(handoffs)} 件

### 最新 Handoff サマリー
```
{summary}
```

> 💡 チャットエクスポートは IDE ネイティブ機能を使用してください。
"""
    else:
        text = f"""## ⚠️ Handoff 未検出

**セッション名**: `{session_name}`
**Handoff ディレクトリ**: `{handoff_dir}`

Handoff ファイルが見つかりません。`/bye` でセッションを終了すると自動生成されます。
"""
    
    return [TextContent(type="text", text=text)]


# PURPOSE: hermeneus_dispatch の処理 — CCL パース + AST 表示 + 実行計画テンプレート
async def _handle_dispatch(args: Dict[str, Any]) -> Sequence[TextContent]:
    """hermeneus_dispatch の処理 — CCL パース + AST 表示 + 実行計画テンプレート"""
    from .dispatch import dispatch
    
    ccl = args["ccl"]
    result = dispatch(ccl)
    
    if not result["success"]:
        text = f"""## ❌ CCL パースエラー

**CCL**: `{ccl}`
**エラー**: {result['error']}

パーサー拡張が必要か、式の修正が必要です。"""
    else:
        text = f"""## ✅ CCL ディスパッチ結果

**CCL**: `{ccl}`

### AST 構造
```
{result['tree']}
```

### 関連ワークフロー
{', '.join(f'`{wf}`' for wf in result['workflows'])}

### 実行計画テンプレート
{result['plan_template']}"""
    
    return [TextContent(type="text", text=text)]


# =============================================================================
# Fallback (MCP なしの場合)
# =============================================================================

# PURPOSE: [L2-auto] MCP SDK がない場合のフォールバック
class FallbackServer:
    """MCP SDK がない場合のフォールバック"""
    
    # PURPOSE: CCL を実行
    async def execute(self, ccl: str, context: str = "") -> Dict[str, Any]:
        """CCL を実行"""
        from .executor import run_workflow
        
        result = await run_workflow(ccl=ccl, context=context)
        return result.to_dict()
    
    # PURPOSE: CCL をコンパイル
    async def compile(self, ccl: str, model: str = "openai/gpt-4o") -> str:
        """CCL をコンパイル"""
        from . import compile_ccl
        return compile_ccl(ccl, model=model)


# =============================================================================
# Entry Point
# =============================================================================

# PURPOSE: MCP サーバーを起動
async def main():
    """MCP サーバーを起動"""
    if not MCP_AVAILABLE:
        print("MCP SDK not available. Install with: pip install mcp", file=sys.stderr)
        print("Running in fallback mode...", file=sys.stderr)
        
        # Simple REPL for testing
        fallback = FallbackServer()
        while True:
            try:
                line = input("hermeneus> ")
                if line.startswith("/"):
                    result = await fallback.execute(line)
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                elif line == "quit":
                    break
            except EOFError:
                break
        return
    
    # MCP サーバーを起動
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


# PURPOSE: エントリーポイント
def run_server():
    """エントリーポイント"""
    asyncio.run(main())


if __name__ == "__main__":
    run_server()
