# MCP Tool Search (defer_loading) 設計文書

> **Status**: Draft (2026-02-15)
> **Priority**: Mid-term (F6)
> **導出**: /eat+ T3-5 (MCP Tool Search)

## 問題定義

| 指標 | 値 |
|:-----|:---|
| MCP サーバー数 | 12+ |
| ツール定義 (推定) | ~134k トークン |
| 全コンテキスト比率 | ~25-35% |
| 影響 | 実質的な作業コンテキストの圧迫 |

現在、全 MCP サーバーのツール定義がセッション開始時にコンテキストに一括ロードされている。 使用しないツールの定義がコンテキスト予算を消費し、BC-18 (コンテキスト予算意識) の N chat messages 閾値に早期到達するリスクがある。

## 解決策: defer_loading + Tool Search

### パターン概要

```
[起動時]
  MCP サーバー登録 → ツール定義をロードしない (defer_loading: true)

[ツール使用時]
  LLM が「このタスクに必要なツールは？」と判断
  → Tool Search API でツール定義を動的取得
  → 必要なツールのみコンテキストに注入
```

### 前提条件

| 条件 | 状態 |
|:-----|:-----|
| MCP SDK の `defer_loading` サポート | ⚠️ Spec 未確認 |
| Antigravity IDE での MCP 設定変更 | ⚠️ 設定可能か未検証 |
| Tool Search API の存在 | [仮説] MCP 仕様に含まれる可能性 |

### 実装ロードマップ

| Phase | 内容 | 推定工数 |
|:------|:-----|:---------|
| **PoC** | 1サーバーで defer_loading テスト | 2h |
| **計測** | 全サーバー on/off でトークン消費比較 | 1h |
| **統合** | 効果が確認されたら全サーバーに適用 | 3h |

## リスク

| リスク | 影響 | 緩和策 |
|:-------|:-----|:-------|
| Tool Search のレイテンシ | ツール呼び出しに遅延 | よく使うツールはピン留め (eager_loading) |
| IDE 非対応 | defer_loading が無視される | IDE 更新を待つ / ワークアラウンド |
| ツール発見精度 | 必要なツールが見つからない | ツール説明文の改善 |

## 次のアクション

1. MCP 公式仕様で `defer_loading` の存在を確認 (`search_web`)
2. Antigravity IDE の MCP 設定フォーマットを調査
3. 1サーバー (gnosis) で PoC を実施

---

*Design v0.1 — /eat+ F6*
