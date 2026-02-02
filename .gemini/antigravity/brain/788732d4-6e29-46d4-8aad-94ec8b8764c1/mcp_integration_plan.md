# MCP 統合計画

## 概要

2つの MCP サーバーを Hegemonikón に統合する。

---

## 1. sequential-thinking MCP

### 状態

- **インストール**: ✅ 完了
- **設定**: ✅ `mcp_settings.json` に登録済み
- **Antigravity 統合**: ✅ 有効

### Hegemonikón マッピング

| 項目 | 値 |
|:-----|:---|
| **Primary** | O1 Noēsis (深い認識) |
| **Secondary** | O3 Zētēsis, A2 Krisis |
| **統合先** | `/noe` ワークフロー |

### 統合方法

```text
/noe 実行時:
  1. 問題を sequential-thinking に渡す
  2. 構造化された思考ステップを取得
  3. 各ステップを /noe の PHASE に対応付け
  4. 再帰的分析を可能に
```

### 期待効果

- 思考プロセスの可視化
- 仮説の反復的検証
- バイアス検出の強化

---

## 2. Redis MCP

### 状態

- **インストール**: 🔄 進行中 (apt-get)
- **サーバー起動**: ⏳ 保留 (要 sudo)
- **MCP 設定**: ⏳ 保留

### Hegemonikón マッピング

| 項目 | 値 |
|:-----|:---|
| **Primary** | H4 Doxa (信念永続化) |
| **Secondary** | H3 Orexis |
| **統合先** | `/bye`, `/boot` ワークフロー |

### 統合方法

```text
/bye 実行時:
  1. 学習した A-matrix を Redis に保存
  2. セッション状態を永続化
  3. 重要な気づきをキャッシュ

/boot 実行時:
  1. Redis から A-matrix を復元
  2. 前回のセッション状態を取得
  3. 継続性を確保
```

### 必要な設定

```json
{
  "mcpServers": {
    "redis": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-redis"],
      "env": {"REDIS_URL": "redis://localhost:6379"}
    }
  }
}
```

---

## 実装優先順位

| 優先 | MCP | 理由 |
|:-----|:----|:-----|
| 1 | sequential-thinking | 既に有効、すぐ使える |
| 2 | Redis | サーバー起動待ち |

---

## 次のアクション

### sequential-thinking (今すぐ)

1. `/noe` で実際に使ってみる
2. 効果を検証
3. 必要なら `/noe.md` に統合手順を追加

### Redis (後日)

1. Redis サーバーを起動 (`sudo systemctl start redis-server`)
2. `mcp_settings.json` に追加
3. `/bye`, `/boot` に統合

---

*計画作成: 2026-01-29*
