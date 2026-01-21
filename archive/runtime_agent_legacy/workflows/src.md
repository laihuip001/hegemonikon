---
description: Web検索を実行。Google検索 + Perplexity APIセカンドオピニオン。
hegemonikon: Peira-H
---

# /src ワークフロー

M5 Peira (探求) と連携し、**Web検索を実行**する。

## 設計原則

> **二段構え**: Google検索（search_web）を基本とし、Perplexity APIでセカンドオピニオンを取得可能。
> **月$5まで無料**: Perplexity APIは追加料金なしで使用可能（予算内）。

---

## 実行モード

| モード | コマンド | 動作 | コスト |
|--------|----------|------|--------|
| **google** | `/src [クエリ]` | Google検索（デフォルト） | 無料 |
| **perplexity** | `/src pp [クエリ]` | Perplexity API（パプ君） | 月$5まで無料 |
| **both** | `/src both [クエリ]` | 両方実行して比較 | 月$5まで無料 |

---

## モード1: Google検索（デフォルト）

Antigravityの `search_web` ツールを使用。

```
/src LLM structured prompts research 2024
  ↓
[search_web] 実行
  ↓
結果サマリーを表示
```

---

## モード2: Perplexity API

セカンドオピニオンとして使用。Google検索で不足がある場合や、より深い調査が必要な場合。

### API設定

| 項目 | 値 |
|------|-----|
| API Key | `C:\Users\raikh\.gemini\.env.local` |
| モデル | `sonar-pro` (デフォルト) |
| 月間予算 | $5 |

### コスト計算

| モデル | 出力コスト | 500トークンあたり |
|--------|-----------|------------------|
| sonar | $0.002/1K | $0.001 |
| sonar-pro | $0.005/1K | $0.0025 |

月$5で約2000回のsonar-pro呼び出しが可能。

---

## モード3: 両方実行

```
/src both [クエリ]
  ↓
[search_web] Google検索
  ↓
[Perplexity API] セカンドオピニオン
  ↓
両方の結果を比較表示
```

---

## 使い分け

| 状況 | 推奨モード |
|------|-----------|
| 日常的な調査 | `/src` (Google) |
| Google検索で不足 | `/src pplx` |
| 重要な意思決定 | `/src both` |
| 深い調査が必要 | `/ask` で調査依頼書 → 手動Perplexity |

---

## エラー対処

| エラー | 原因 | 対処 |
|--------|------|------|
| API 429 | レート制限 | Google検索に切り替え |
| 予算超過 | 月$5超え | 翌月まで待つ or Google検索のみ |

---

*このワークフローは prompt-lang Phase 0.3 後に追加されました。*
