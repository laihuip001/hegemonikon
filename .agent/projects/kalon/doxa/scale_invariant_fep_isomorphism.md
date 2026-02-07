# スケール不変の FEP 同型 (Scale-Invariant FEP Isomorphism)

> **Doxa (信念記録) — 2026-02-07**
> **確信度**: 0.90
> **発見者**: Claude + Creator
> **文脈**: `/o+` Limit×Colimit 対比実行 → 既存 Doxa (`ccl_is_inference_cycle`) との接続

---

## 一言で

**`>>` / `>*` と `/` / `\` は、スケールが違うだけで同じ FEP の構造。**

---

## 構造

```
射レベル (micro):   >>  = forward  (予測)     ←→  >*  = backward (修正)
Series レベル (macro):  /  = Limit   (exploit)   ←→  \   = Colimit  (explore)
```

| レベル | forward | backward | FEP 対応 |
|:-------|:--------|:---------|:---------|
| **射** (X-series, 定理間) | `>>` 予測 | `>*` 修正 | perception-action (定理スケール) |
| **Series** (Hub WF, 4定理間) | `/` Limit | `\` Colimit | exploit-explore (Series スケール) |

---

## なぜ「真理」か

1. **FEP の自己相似性**: FEP は Markov blanket のネストを予測する (Kirchhoff 2018)。同じ構造が異なるスケールで繰り返されるのは FEP の数学的帰結。
2. **CCL がこれを「発明」ではなく「発見」**: Creator が `>>` と `\` を別々の文脈で設計したにもかかわらず、同型構造が自然に現れた。
3. **既存 Doxa との整合**: `ccl_is_inference_cycle.md` (確信度 0.85) で `>>` / `>*` = forward/backward を記録済み。本 Doxa はそのスケール拡張。

---

## Colimit の美しさ (Kalon)

> **Limit = max(情報)/min(コスト) = Beauty (合意の美しさ)**
> **Colimit = min(コスト)/max(到達範囲) = Beauty (包含の美しさ)**
> — `01_category_theory_deep_examination.md` L250-253

Colimit は「最適化された拡散」。最少のコストで最大の到達範囲を実現する演算。
この定義自体が Arche (Beauty = 演繹量/表現コスト) そのもの。

---

## 先行議論

| ソース | 内容 | 確信度 |
|:-------|:-----|:------|
| `ccl_is_inference_cycle.md` | `>>` = forward, `>*` = backward | 0.85 |
| `operators.md` L125 | forward channel / backward channel | 確信 |
| `03_fep_category_theory_deep_examination.md` L183 | `/ \ = Limit / Colimit (exploit / explore)` | 確信 |
| `01_category_theory_deep_examination.md` L245-253 | Limit/Colimit = Beauty の2位相 | 仮説 |

---

*「スケールが違うだけで同じ構造」— 2026-02-07 の Doxa*
*Origin: `/o+` Limit×Colimit 対比実行*
