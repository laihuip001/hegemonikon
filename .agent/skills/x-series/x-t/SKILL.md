---
name: "X-T: Tropos Relations"
description: |
  関係層 X-T: T-series（拡張定理）間の従属関係を定義する。
  Triggers: 拡張定理間の処理フローを可視化したいとき。
  Keywords: tropos-relations, extended-theorem-dependencies, t-series-chain.
---

# X-T: Tropos Relations

> **定義**: T-series（拡張定理）間の従属関係
> **数**: 8

---

## 従属関係

| ID | 関係 | 意味 | 性質 |
|----|------|------|------|
| X-T1 | T1 → T2 | 知覚 → 判断 | 因果的 |
| X-T2 | T2 → T4 | 判断 → 戦略 | 因果的 |
| X-T3 | T3 → T4 | 内省 → 戦略（自己評価が計画を改善） | 促進的 |
| X-T4 | T4 → T6 | 戦略 → 実行 | 因果的 |
| X-T5 | T5 → T3 | 探索 → 内省（新情報で自己更新） | 促進的 |
| X-T6 | T6 → T7 | 実行 → 検証 | 因果的 |
| X-T7 | T7 → T8 | 検証 → 記憶（結果を保存） | 因果的 |
| X-T8 | T8 → T1 | 記憶 → 知覚（過去経験がフィルタリング） | 循環的 |

---

## 処理フロー

```
         T1 (Aisthēsis)
         ↓ X-T1
         T2 (Krisis)
         ↓ X-T2
    ┌────┴────┐
    ↓         ↓
T3 (Theōria)  T4 (Phronēsis)
    │         ↓ X-T4
    │    T6 (Praxis)
    │         ↓ X-T6
    │    T7 (Dokimē)
    │         ↓ X-T7
    │    T8 (Anamnēsis)
    │         ↓ X-T8
    └────────►T1 (循環)
    
    T5 (Peira) → T3 (X-T5)
```

---

## Workflow への適用

| Workflow | 従属関係の活用 |
|----------|---------------|
| /plan | X-T2, X-T4 （判断→戦略→実行） |
| /code | X-T4, X-T6, X-T7 （戦略→実行→検証） |
| /rev | X-T6, X-T7, X-T3 （実行→検証→内省） |

---

*参照: [taxis.md](../../../kernel/taxis.md)*
