---
description: 見る — /s*%/dia
version: 1.0.0
lcm_state: beta
---

version: 1.0.0
lcm_state: beta
# @scan — 見る

> **CCL**: `@scan = /s*%/dia`
> **俗名**: 見る
> **目的**: 設計と判定を同時に収束+展開し、状況の全体像と要約を一撃で得る

---

version: 1.0.0
lcm_state: beta
## 本質

> 「森と木を同時に見る」

- **収束 (`*`)**: 設計と判定を融合 → 1つの状況判断
- **展開 (`%`)**: 設計の全次元 × 判定の全次元 → マトリクス

---

version: 1.0.0
lcm_state: beta
## CCL 展開

```ccl
@scan = /s *% /dia
```

### 出力形式

```
[収束] /s*/dia = "設計状態を判定基準で融合 → 総合評価スコア"
[展開] /s%/dia =
  | s\dia      | PASS     | WARN     | FAIL     |
  |------------|----------|----------|----------|
  | 構造設計   | ...      | ...      | ...      |
version: 1.0.0
lcm_state: beta
  | 実装方針   | ...      | ...      | ...      |
  | テスト戦略 | ...      | ...      | ...      |
  | リソース   | ...      | ...      | ...      |
```

---

version: 1.0.0
lcm_state: beta
## 使用場面

| トリガー | 説明 |
|:---------|:-----|
| PJ の現状を素早く把握したい | `/now` より深く、`/dia` より広く |
version: 1.0.0
lcm_state: beta
| レビュー前の全体確認 | 一撃で問題点と全体像を把握 |
| セッション冒頭の状況確認 | Boot 後の追加分析として |

---

version: 1.0.0
lcm_state: beta
## 演算子適用

```ccl
@scan+    # 全次元を詳細展開
@scan-    # 収束のみ (展開省略)
@scan{target="PJ名"}  # 特定 PJ にスコープ
```

---

version: 1.0.0
lcm_state: beta
## 複雑度

| 演算子 | pt |
|:-------|:--:|
| `@scan` | 6 |
version: 1.0.0
lcm_state: beta

> `*%` の基本コスト。

---

version: 1.0.0
lcm_state: beta
*v1.0 — FuseOuter マクロ初版 (2026-02-13)*
