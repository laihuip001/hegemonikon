---
name: "X-O: Ousia Relations"
description: |
  関係層 X-O: O-series（純粋定理）間の従属関係を定義する。
  Triggers: 純粋定理間の因果連鎖を可視化したいとき。
  Keywords: ousia-relations, pure-theorem-dependencies, o-series-chain.
---

# X-O: Ousia Relations

> **定義**: O-series（純粋定理）間の従属関係
> **数**: 4

---

## 従属関係

| ID | 関係 | 意味 | 性質 |
|----|------|------|------|
| X-O1 | O1 → O2 | 世界モデル更新 → 選好モデル更新 | 因果的 |
| X-O2 | O2 → O4 | 目標推論 → 目標行為 | 因果的 |
| X-O3 | O3 → O1 | 情報行為 → 情報推論 | 因果的 |
| X-O4 | O4 → O3 | 目標行為 → 情報行為（フィードバック） | 循環的 |

---

## 循環構造

```
    O1 (Noēsis)
    ↓ X-O1
    O2 (Boulēsis)
    ↓ X-O2
    O4 (Energeia)
    ↓ X-O4
    O3 (Zētēsis)
    ↓ X-O3
    O1 (Noēsis)
    ↻ 循環
```

---

## 1:3 ピラミッド

- 論文を読む(O1) → 優先順位を決める(O2)
- 優先順位を決める(O2) → コードを書く(O4)
- 実験する(O3) → 結果を理解する(O1)

---

*参照: [taxis.md](../../../kernel/taxis.md)*
