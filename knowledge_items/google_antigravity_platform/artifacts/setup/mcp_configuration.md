# MCP Server Configuration

## Critical: Key Name

> **`mcpServers` が唯一有効なキー。`servers` キーは IDE に無視される。**
>
> 検証日: 2026-02-10。`servers` キーで 9 サーバーを定義 → IDE パネル 0/100 tools。
> `mcpServers` に統合 → 31/100 tools、全 9 サーバー接続成功。

## Config Location

`~/.gemini/antigravity/mcp_config.json`

## Config Format

```json
{
  "mcpServers": {
    "server-name": {
      "command": "/path/to/python",
      "args": ["/path/to/mcp_server.py"],
      "description": "Tool description for LLM"
    }
  }
}
```

## IDE Panel Access

`Ctrl+Shift+P` → `Antigravity: Manage MCP Servers`

## Tool Limit

- IDE 上限: **100 tools**
- 推奨: サーバーあたり **20 tools 以下**
- 2026-02-10 時点: 31/100 (9 servers)

## Transport

- **stdio**: ローカルプロセス (推奨、現在使用中)
- **SSE/HTTP**: リモートサーバー用 (未使用)

## Resources

MCP Resources (`list_resources` / `read_resource`) は MCP サーバー側で公開可能だが、
**2026-02-10 時点で Claude エージェントからの直接呼出は IDE が未対応**。
IDE の `list_resources` / `read_resource` ツールは `server name not found` を返す。
回避策: ツールに統合して同じデータを返す。

## Hot Reload

MCP サーバーの変更時は **IDE 再起動が必要**。
「Manage MCP Servers」パネルの「Refresh」ボタンでは新規サーバーを検出できない。

## Lessons Learned

1. ドキュメントより実測を信じよ
2. `servers` vs `mcpServers` — 一文字の違いで全機能が死ぬ
3. IDE パネルの「0/100 tools」は全サーバー未接続を意味する
