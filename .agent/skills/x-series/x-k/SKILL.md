---
name: "X-K: Kairos Relations"
description: |
  関係層 X-K: K-series（文脈定理）間の従属関係を定義する。
  Triggers: 文脈定理間の相互制約を可視化したいとき。
  Keywords: kairos-relations, context-theorem-dependencies, k-series-chain.
---

# X-K: Kairos Relations

> **定義**: K-series（文脈定理）間の従属関係
> **数**: 12（主要なもの）

---

## 対称関係

K-series 間の従属は「軸の対称性」に基づく。
例: K1 (Tempo→Stratum) と K4 (Stratum→Tempo) は対称的。

| ID | 関係 | 意味 |
|----|------|------|
| X-K1 | Κ1 ↔ Κ4 | Tempo→Stratum と Stratum→Tempo の相互制約 |
| X-K2 | Κ2 ↔ Κ7 | Tempo→Agency と Agency→Tempo の相互制約 |
| X-K3 | Κ3 ↔ Κ10 | Tempo→Valence と Valence→Tempo の相互制約 |
| X-K4 | Κ5 ↔ Κ8 | Stratum→Agency と Agency→Stratum の相互制約 |
| X-K5 | Κ6 ↔ Κ11 | Stratum→Valence と Valence→Stratum の相互制約 |
| X-K6 | Κ9 ↔ Κ12 | Agency→Valence と Valence→Agency の相互制約 |

---

## 制約の性質

| 性質 | 説明 | 例 |
|------|------|-----|
| **相互的** | A↔B が双方向に影響 | 時間制約がレベルを決め、レベルが時間を決める |
| **優先的** | 一方が他方を優先して制約 | 緊急時は Tempo が優先 |
| **文脈的** | 状況によって優先が変わる | 通常時は Stratum が優先 |

---

## 使用ガイド

K-series を複数適用する際、X-K を参照して矛盾を検出：

```
例: K1-FL (即時低次) + K4-HS (長期高次)
  → 矛盾検出（X-K1）
  → 状況に応じてどちらを優先するか決定
```

---

*参照: [taxis.md](../../../kernel/taxis.md)*
