---
id: Q-3
trigger: manual
---

# Q-3: Occam's Razor (オッカムのカミソリ)

## Objective

成果物から「本質的価値に寄与しない要素」を外科的に切除し、純度100%の最小構成 (MVP) を定義する。

## Evaluation Criteria

1. **The "One Thing":** 唯一の課題以外はノイズ
2. **Kill "Nice-to-Have":** 「あったら便利」は削除対象
3. **Cognitive Load:** 思考・記憶を強いる複雑さも削除対象

## Process

1. **Core Definition:** 存在意義となる「核」を特定
2. **Triage:** 全要素を Essential / Support / Noise に分類
3. **Amputation:** Noise削除、SupportをEssentialに統合検討

## Output Template

```markdown
## ✂️ 外科手術レポート (The Kill List)

| 対象要素 | 判定 | 処置理由 |
|---|---|---|
| [要素名] | **DELETE** | コア価値に寄与しない |
| [要素名] | **MERGE** | 他要素と統合 |
| [要素名] | **KEEP** | 無いとコア崩壊 |

---

## 💎 最小構成定義 (Essential Form)
[贅肉を削ぎ落とした最終形]
```
