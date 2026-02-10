# MCP Gateway 設計書 — synedrion/

> **Source:** IBM/mcp-context-forge, SEP-1960, WordPress Abilities API
> **Purpose:** Jules と外部MCP群を安全に束ねるGatewayの設計

---

## 概要

synedrion（評議会）内に MCP Gateway を配置し、外部 MCP サーバー群への
アクセスを一元管理する。認証・ツール名前空間・セキュリティポリシーを
Gateway 層で集約し、Jules および他のエージェントは Gateway 経由でのみ
外部ツールにアクセスする。

---

## アーキテクチャ

```
┌──────────────────────────────────────────┐
│  Jules / Claude / Antigravity IDE        │
│  (MCP クライアント)                       │
└──────────────┬───────────────────────────┘
               │ MCP Protocol (stdio)
               ▼
┌──────────────────────────────────────────┐
│  synedrion MCP Gateway                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │Discovery │ │Auth Proxy│ │Policy    │ │
│  │Engine    │ │(OAuth2.1)│ │Enforcer  │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       │            │            │        │
│  ┌────┴────────────┴────────────┴────┐   │
│  │       Virtual MCP Server          │   │
│  │   (名前空間統合・ルーティング)       │   │
│  └────┬─────────────┬───────────┬────┘   │
└───────┼─────────────┼───────────┼────────┘
        │             │           │
   ┌────┴────┐  ┌─────┴───┐  ┌───┴─────┐
   │ gnosis  │  │ sophia  │  │ external│
   │ MCP     │  │ MCP     │  │ MCP     │
   └─────────┘  └─────────┘  └─────────┘
```

---

## コンポーネント仕様

### 1. Discovery Engine

**目的:** URL を渡されるだけでサーバーの能力を自動発見。

**プロトコル:** SEP-1960 `.well-known/mcp`

```python
async def discover(base_url: str) -> ServerCapabilities:
    """
    1. GET {base_url}/.well-known/mcp を試行
    2. レスポンスから capabilities, transport, auth を抽出
    3. Gateway のルーティングテーブルに自動登録
    """
    response = await http_get(f"{base_url}/.well-known/mcp")
    return ServerCapabilities(
        mcp_version=response["mcpVersion"],
        tools=response.get("capabilities", {}).get("tools"),
        resources=response.get("capabilities", {}).get("resources"),
        auth=response.get("authentication"),
    )
```

**`.well-known/mcp` レスポンス例:**

```json
{
  "mcpVersion": "2024-11-05",
  "capabilities": {
    "tools": { "endpoint": "/mcp/tools" },
    "resources": { "endpoint": "/mcp/resources" }
  },
  "authentication": {
    "type": "oauth2",
    "authorizationUrl": "https://example.com/oauth/authorize"
  }
}
```

### 2. Auth Proxy

**目的:** ユーザー認証を Gateway 層で集約し、下流に委譲。

| 機能 | 実装 |
|:-----|:-----|
| ユーザー認証 | JWT / OAuth 2.1 |
| 認証伝播 | `X-Upstream-Authorization` ヘッダー |
| スコープ制限 | 許可されたツールのみ転送 |

### 3. Policy Enforcer

**目的:** ツール呼び出しのセキュリティポリシーを強制。

```yaml
# policy.yaml
policies:
  - name: "destructive-operations-guard"
    match:
      tools: ["delete_*", "drop_*", "rm_*"]
    require:
      human_approval: true
      log_level: "audit"
  
  - name: "rate-limit"
    match:
      tools: ["*"]
    limit:
      requests_per_minute: 60
  
  - name: "allowed-servers"
    servers:
      allow: ["gnosis", "sophia", "hermeneus", "sympatheia", "mneme"]
      deny: ["*"]  # 未登録サーバーはデフォルト拒否
```

### 4. Virtual MCP Server

**目的:** 複数の下流 MCP サーバーを束ね、単一の仮想サーバーとして公開。

| 機能 | 詳細 |
|:-----|:-----|
| 名前空間 | `server_name.tool_name` でプレフィックス付与 |
| ルーティング | ツール名からサーバーを逆引き |
| エラー伝播 | 下流エラーを統一フォーマットで返却 |

---

## Abilities パターン (CMS Adapter 由来)

WordPress Abilities API のパターンを anamnesis/ の知識ベースに適用:

```python
# 概念コード: Knowledge Abilities
abilities = {
    "hgk.query_concept": {
        "description": "Sophia KI を検索",
        "input_schema": {"query": "string", "limit": "integer"},
        "permission": "read",
        "backend": "sophia_mcp",
    },
    "hgk.append_journal": {
        "description": "Kairos にジャーナルエントリを追加",
        "input_schema": {"content": "string", "tags": "array"},
        "permission": "write",
        "backend": "kairos_ingest",
    },
}
# → MCP Adapter が abilities を走査して ListTools スキーマを自動生成
```

---

## 実装ロードマップ

| Phase | 内容 | 時期 |
|:------|:-----|:-----|
| **0. 設計** | 本ドキュメント（完了） | 2026-02-10 |
| 1. Policy YAML | `synedrion/policy.yaml` 定義 | 次回 |
| 2. Virtual Server | 既存 MCP を束ねる PoC | 将来 |
| 3. Discovery | `.well-known/mcp` プローブ | 将来 |
| 4. Auth Proxy | OAuth 2.1 統合 | 将来 |

---

## 参考

- [IBM/mcp-context-forge](https://github.com/IBM/mcp-context-forge) — Gateway & Registry
- [SEP-1960: Server Discovery](https://www.ekamoira.com/blog/mcp-server-discovery-implement-well-known-mcp-json-2026-guide)
- [WordPress Abilities API](https://developer.wordpress.org/news/2026/02/from-abilities-to-ai-agents-introducing-the-wordpress-mcp-adapter/)
- [Anthropic: Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)

---

*v1.0 — MCP Gateway Design (2026-02-10)*
