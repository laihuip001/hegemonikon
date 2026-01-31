# mekhane/mcp/ PROOF

> **存在証明**: MCP (Model Context Protocol) サーバー群を格納

## 必然性の導出

```
Hegemonikón は外部アプリケーションと連携する
→ MCP プロトコルでの公開が必要
→ mcp/ ディレクトリが担う
```

## 粒度

**L2/インフラ**: 定理機能を外部公開するインターフェース

## 主要ファイル

| File | 公開対象 |
|------|---------|
| `gnosis_mcp_server.py` | 知識検索 |
| `sophia_mcp_server.py` | 研究調査 |
| `jules_mcp_server.py` | Jules API |
| `digestor_mcp_server.py` | 消化処理 |
| `mneme_server.py` | 記憶管理 |
