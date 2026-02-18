# MCP Tool Search (defer_loading) 設計文書

> **Status**: PoC 調査完了 (2026-02-15)
> **Priority**: Mid-term (F6)
> **導出**: /eat+ T3-5 (MCP Tool Search)

## 問題定義

| 指標 | 値 |
|:-----|:---|
| MCP サーバー数 | 12+ (gnosis, sophia, jules, typos, digestor, sympatheia, hermeneus, mneme, ochema, filesystem, exa, memory, playwright, sequential-thinking) |
| ツール定義 (推定) | ~134k トークン |
| 全コンテキスト比率 | ~25-35% |
| 影響 | 実質的な作業コンテキストの圧迫 |

現在、全 MCP サーバーのツール定義がセッション開始時にコンテキストに一括ロードされている。 使用しないツールの定義がコンテキスト予算を消費し、BC-18 (コンテキスト予算意識) の N chat messages 閾値に早期到達するリスクがある。

## PoC 調査結果 (2026-02-15)

### MCP 仕様確認

| 項目 | 結果 |
|:-----|:-----|
| `defer_loading` の存在 | ✅ MCP Beta 機能として確認 |
| トークン削減効果 | 最大 85% (文献報告) |
| IDE サポート | ⚠️ Antigravity IDE での設定可能性は未検証 |
| GitHub Issue | Tool 構造体への `DeferLoading` boolean プロパティ追加が議論中 |

### 現在の MCP 設定構造

| ファイル | 内容 | サーバー数 |
|:---------|:-----|:---------:|
| `.gemini/antigravity/mcp_config.json` | IDE 主要設定 (gnosis, sophia, jules, 他) | 12+ |
| `.config/Antigravity/User/mcp.json` | IDE ユーザー設定 (GitKraken) | 1 |
| `.vscode/mcp.json` | ワークスペース設定 (gnosis, hermeneus) | 2 |

現在の設定に `defer_loading` フィールドは一切使用されていない。

### defer_loading パターン

```jsonc
// 仮説: IDE が対応していれば以下で有効化
{
  "mcpServers": {
    "gnosis": {
      "command": "...",
      "args": ["..."],
      "defer_loading": true    // ← 追加
    }
  }
}
```

### PoC 方針

| Phase | 内容 | ブロッカー |
|:------|:-----|:----------|
| **P0** | IDE が `defer_loading` を解釈するか確認 | IDE ソースコード or ドキュメント参照が必要 |
| **P1** | 1サーバー (typos) で `defer_loading: true` テスト | P0 の結果次第 |
| **P2** | 効果測定: ツール定義トークン before/after | P1 成功後 |

### 結論

> [!IMPORTANT]
> `defer_loading` は MCP 仕様として存在するが、**Antigravity IDE が解釈するかは未確認**。
> IDE のソースコードまたはドキュメントで `defer_loading` の処理を確認する必要がある。
> 現時点では **PoC ブロック状態** — IDE 側の対応調査が先行課題。

## リスク

| リスク | 影響 | 緩和策 |
|:-------|:-----|:-------|
| Tool Search のレイテンシ | ツール呼び出しに遅延 | よく使うツールはピン留め (eager_loading) |
| IDE 非対応 | defer_loading が無視される | IDE 更新を待つ / ワークアラウンド |
| ツール発見精度 | 必要なツールが見つからない | ツール説明文の改善 |

## 次のアクション

1. ~~MCP 公式仕様で `defer_loading` の存在を確認~~ ✅ 確認済み (Beta)
2. **Antigravity IDE のソースで `defer_loading` の処理を調査** (ブロッカー)
3. P0 クリア後: 1サーバー (typos) で PoC を実施

---

*Design v0.2 — PoC 調査完了 (2026-02-15)*
