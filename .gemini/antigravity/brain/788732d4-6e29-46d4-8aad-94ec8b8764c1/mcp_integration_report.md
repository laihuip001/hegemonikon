# MCP 統合調査・実装レポート

## 調査結果 (Perplexity)

### 核心問題

**`alwaysAllow` が空配列だったため、MCP ツールが LLM の context に含まれていなかった**

### 解決策

```json
// 修正前
"alwaysAllow": []

// 修正後
"alwaysAllow": ["sequentialthinking"]
```

---

## 実装済み

### 1. mcp_settings.json 修正 ✅

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "disabled": false,
      "alwaysAllow": ["sequentialthinking"]
    }
  }
}
```

### 2. MCP サーバー起動確認 ✅

```
Sequential Thinking MCP Server running on stdio
```

---

## 次のステップ

1. **Antigravity IDE を再起動** (設定を反映)
2. **MCP ツールが私のツールセットに現れるか確認**
3. **`/noe` で sequentialthinking を呼び出してみる**

---

## 代替アプローチ (MCP が認識されない場合)

### 方案 A: run_command 経由

```python
import subprocess
import json

def invoke_sequential_thinking(query: str) -> dict:
    result = subprocess.run([
        "npx", "-y", "@modelcontextprotocol/server-sequential-thinking"
    ], input=json.dumps({"method": "think", "params": {"input": query}}),
       capture_output=True, text=True)
    return json.loads(result.stdout)
```

### 方案 B: Antigravity MCP Store

- Antigravity UI → `...` → MCP → Manage MCP Server
- "Sequential Thinking" を MCP Store から追加

---

## 学んだこと

| 発見 | 意味 |
|:-----|:-----|
| `alwaysAllow` が重要 | 空配列だとツールが公開されない |
| MCP Inspector | `npx @modelcontextprotocol/inspector` でデバッグ可能 |
| Tool overload | 40+ ツールで LLM が見落とす |
| プロンプトで明示 | ツール名を指定すると呼び出されやすい |

---

*レポート作成: 2026-01-29*
