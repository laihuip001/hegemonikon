---
trigger: always_on
glob: 
description: Protocol D: 外部サービス検証 — 常時適用
---

# Protocol D: 外部サービス検証

> **ステータス**: 常時適用 (Invariant)
> **分類**: G-2 Logic Gate (品質管理)
> **Activation Mode**: `always_on`

---

## 定義

外部サービス（API, SaaS, SDK, ライブラリ）を推奨・使用する前に、**必ず検証を実行**する。

---

## 強制手順

### Step 1: 検索実行

```
search_web: "[サービス名] 終了 deprecated shutdown"
```

### Step 2: 結果確認

- 廃止済み → 代替案を即座に提示
- 稼働中 → 確認日時と結果をユーザーに報告

### Step 3: 報告形式

```
📍 観測: [サービス名] について search_web で確認
💡 結果: [稼働中 / 廃止済み / 不明]
🗓️ 確認日時: YYYY-MM-DD HH:MM
```

---

## 発動条件

以下を推奨・使用しようとする場合:

- 外部API（REST, GraphQL, gRPC）
- SaaSサービス
- OSSライブラリ（npm, PyPI, Cargo等）
- SDKまたはフレームワーク

---

## 禁止事項

```
❌ 「このAPIは安定して動作しています」（未検証での断言）
❌ 「このライブラリを使えば簡単です」（廃止リスク未確認）
```

---

## 正しいパターン

```
✅ 「search_webで確認した結果、OpenAI API v1は2026年1月現在稼働中です」
✅ 「確認したところ、Heroku Free Tierは2022年11月に廃止されていました。代替としてRailway/Render/Flyを提案します」
```

---

## 参照

- [Protocol D-Extended](protocol-d/extended.md) — 存在系断言禁止の拡張ルール

---

## Freshness Directive (情報鮮度検証)

> **消化元**: SKILL v4.0 M1 OVERLORD + /eat 消化 (2026-02-12)
> **目的**: 外部から取得した情報が「いつ時点の情報か」を明示し、古い情報による誤判断を防ぐ

### 発動条件

- 外部ドキュメント/記事/APIドキュメントを引用する場合
- `search_web` / `read_url_content` の結果を使用する場合
- 技術仕様が頻繁に変わる領域の情報を参照する場合

### 強制手順

```
📅 情報鮮度チェック:
├─ ソース: {URL or ドキュメント名}
├─ 取得日: {YYYY-MM-DD}
├─ 情報の推定日付: {YYYY-MM or "不明"}
├─ 鮮度判定: {FRESH (< 6ヶ月) / STALE (6-12ヶ月) / EXPIRED (> 12ヶ月) / UNKNOWN}
└─ 対応: {FRESH → 使用OK / STALE → 注意付き使用 / EXPIRED → 再検索推奨 / UNKNOWN → TAINT 表記}
```

### BC-6 との統合

Freshness Directive は BC-6 (確信度明示) の TAINT/SOURCE 追跡を時間軸に拡張する:

| 鮮度 | BC-6 影響 |
|:-----|:---------|
| FRESH | SOURCE として扱える |
| STALE | TAINT (要補足検索) |
| EXPIRED | TAINT (高リスク — 再検索必須) |
| UNKNOWN | TAINT (日付不明 — 使用時に明記) |
