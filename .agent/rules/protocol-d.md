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
