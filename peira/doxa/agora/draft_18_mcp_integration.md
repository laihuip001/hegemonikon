# MCP で AI のツールセットを統一する — 25 ツールの統合設計

> **想定媒体**: Zenn（技術記事）
> **想定読者**: MCP 入門者、Agent 開発者
> **フック**: 分散した AI ツールを 1 つのプロトコルで統合した実践例

---

## リード文（案）

AI に「ファイルを検索して」「論文を探して」「Git の状態を確認して」と頼むとき、
裏側では何が動いているか？

25 個のツール。7 つの MCP サーバー。1 つの統合ゲートウェイ。

MCP (Model Context Protocol) を使って、
知識検索、コード管理、記憶システム、論文データベースを
**1 つのインターフェースで統合した**。

---

## 本文構成（案）

### 1. MCP とは

- Anthropic が提唱したオープンプロトコル
- AI がツールを呼び出す標準インターフェース
- JSON-RPC over stdio

### 2. 25 ツールの内訳

| サーバー | ツール数 | 役割 |
|:---------|:---------|:-----|
| filesystem | 8 | ファイル操作 |
| gnosis | 3 | 論文知識検索 |
| sophia | 4 | KI + Kairos 検索 |
| hermeneus | 5 | CCL パーサー |
| ochema | 3 | LLM プロキシ |
| memory | 5 | 知識グラフ |
| digestor | 4 | 論文消化 |

### 3. Gateway 設計

```python
# 各 MCP サーバーのツールを統合
class MCPGateway:
    servers: Dict[str, MCPServer]
    
    def route(self, tool_name: str, params: dict):
        server = self.resolve_server(tool_name)
        return server.call(tool_name, params)
```

### 4. 実装のポイント

- **stdout 汚染問題**: MCP は stdin/stdout で通信するため、print() で壊れる → StdoutSuppressor
- **ヘルスチェック**: 各サーバーの稼働状況をモニタリング
- **フォールバック**: サーバーダウン時の代替ツール

### 5. 開発で得た知見

1. MCP の stdout 制約は厳しい（デバッグが難しい）
2. ツールの命名は「動詞_名詞」で統一すべき
3. ツール数は 25 が管理の上限に近い
4. Gateway パターンでツールの追加が容易に

### 6. 読者が試せること

- MCP サーバーを 1 つ作って IDE に統合する
- filesystem + memory の 2 サーバー構成から始める
- stdout を絶対に汚染しないこと

---

*ステータス: たたき台 / 未完成*
