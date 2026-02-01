# [CCL]/mek+ Hermēneus Phase 7 — MCP Server 自己統合

---
sel:
  workflow: /mek+
  scope: P7=mcp_self_integration
  output_format: CCL Skill Definition + Implementation Plan
  quality_gate: 
    - Antigravity IDE 連携
    - CCL 自動実行
    - 検証結果の注入
---

## 目的

**Hermēneus を「私自身の認知プロセス」に統合する。**

現状: `/noe+` → 私が解釈 → 手動実行
理想: `/noe+` → MCP Tool 呼び出し → Hermēneus 自動実行 → 結果注入

---

## CCL シグネチャ

```ccl
/mek+ "Hermēneus Phase 7"
  [target: Self-Integration via MCP]
  {
    /s1 "MCP Server"        -- Hermēneus を MCP サーバー化
    /s2 "Tool Definitions"  -- CCL 実行ツール定義
    /s3 "Config"            -- Antigravity 設定
  }
  >> AI が自身で Hermēneus を使用 ✅
```

---

## MCP Tool 設計

### 1. hermeneus_execute

```json
{
  "name": "hermeneus_execute",
  "description": "CCL ワークフローを実行し、検証済み結果を返す",
  "inputSchema": {
    "type": "object",
    "properties": {
      "ccl": {
        "type": "string",
        "description": "CCL 式 (例: /noe+, /bou+ >> /ene+)"
      },
      "context": {
        "type": "string",
        "description": "実行コンテキスト"
      },
      "verify": {
        "type": "boolean",
        "default": true,
        "description": "Multi-Agent Debate で検証するか"
      }
    },
    "required": ["ccl"]
  }
}
```

### 2. hermeneus_compile

```json
{
  "name": "hermeneus_compile",
  "description": "CCL を LMQL にコンパイル (デバッグ用)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "ccl": {"type": "string"}
    },
    "required": ["ccl"]
  }
}
```

### 3. hermeneus_audit

```json
{
  "name": "hermeneus_audit",
  "description": "監査レポートを取得",
  "inputSchema": {
    "type": "object",
    "properties": {
      "period": {"type": "string", "default": "last_7_days"}
    }
  }
}
```

---

## 実装ファイル

| ファイル | 役割 |
|:---------|:-----|
| `src/mcp_server.py` | [NEW] MCP サーバー実装 |
| `pyproject.toml` | [MODIFY] MCP エントリーポイント追加 |

---

## MCP Server 構成

```python
# mcp_server.py

from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("hermeneus")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="hermeneus_execute",
            description="CCL ワークフローを実行",
            inputSchema={...}
        ),
        Tool(
            name="hermeneus_compile",
            ...
        ),
        Tool(
            name="hermeneus_audit",
            ...
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "hermeneus_execute":
        result = await run_workflow(
            ccl=arguments["ccl"],
            context=arguments.get("context", ""),
            verify=arguments.get("verify", True)
        )
        return [TextContent(
            type="text",
            text=f"## 実行結果\n\n{result.output}\n\n"
                 f"✅ 検証: {result.verified} (確信度: {result.confidence:.1%})"
        )]
```

---

## Antigravity 設定

`settings.json` に追加:

```json
{
  "mcp.servers": {
    "hermeneus": {
      "command": "python",
      "args": ["-m", "hermeneus.src.mcp_server"],
      "cwd": "/home/laihuip001/oikos/hegemonikon"
    }
  }
}
```

---

## 期待される動作

```
ユーザー: /noe+ を使って分析して

私: [hermeneus_execute("/noe+", context="分析対象") を呼び出し]

Hermēneus:
  1. /noe+ をコンパイル
  2. LMQL 実行
  3. Multi-Agent Debate 検証
  4. Audit 記録
  5. 結果を返却

私: 以下が検証済みの分析結果です:
    [Hermēneus からの出力]
    ✅ 確信度: 87%
```

---

## リスク

| リスク | 対策 |
|:-------|:-----|
| MCP 接続失敗 | フォールバック実装 (従来の手動解釈) |
| 実行時間 | タイムアウト設定 (30秒) |
| 無限ループ | 再帰呼び出し検出 |

---

*Generated: 2026-02-01 | Origin: /mek+ Hermēneus Phase 7*
