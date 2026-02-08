---
title: "Precision Weighting Gap — FEP 推論サイクルの欠落ステップ"
created: "2026-02-08T10:51:00+09:00"
source: "Creator 対話: HGK の存在意義の再検討"
confidence: 0.80
related:
  - kernel/SACRED_TRUTH.md
  - kernel/axiom_hierarchy.md
  - .agent/projects/kalon/doxa/ccl_is_inference_cycle.md
  - .agent/projects/kalon/doxa/derivative_meta_cycle_hypothesis.md
tags: [fep, precision-weighting, design-gap, implementation]
---

## 発見

HGK は FEP (L0公理) から演繹された体系だが、FEP 推論サイクルの4ステップのうち **Precision Weighting だけが「座標」(静的構造) に留まり、「操作」(動的重みづけ) に昇格していない**。

## FEP 推論サイクルの HGK 実装状況

| FEP ステップ | HGK 実装 | 種類 | 状態 |
|:------------|:---------|:-----|:----:|
| Prediction | `>>` 演算子 | 操作 ✅ | 実装済 |
| Prediction Error | `>*` 演算子 | 操作 ✅ | 実装済 |
| Model Update | `/dox`, `/epi` | 操作 ✅ | 実装済 |
| **Precision Weighting** | Precision 座標 (C↔U) | **構造のみ** ⚠️ | **未実装** |

## 部分的な既存実装

| 部品 | 役割 | Precision Weighting の何に相当するか |
|:-----|:-----|:----------------------------------|
| `+` / `-` | 精度パラメータの上下 | 実行手段 |
| H2 Pistis | 確信度評価 | 評価基準 |
| V[] 閾値 | explore/exploit 判定 | 二値的近似 |
| Hub WF (Peras) | 4定理の暗黙的重みづけ | 暗黙的に含むが明示化されていない |

## 設計時精度 vs 実行時精度

| | 設計時精度 (座標) | 実行時精度 (PW) |
|:--|:---------------|:---------------|
| 何が決めるか | Precision 座標値 | 今この瞬間の文脈 |
| いつ決まるか | 定理定義時 | 実行時 |
| 例 | O=低精度, A=高精度 | O1の直観が鋭い瞬間→高精度 |
| HGK の状態 | ✅ 実装済 (座標) | ⚠️ 未実装 |

## 洞察

HGK の存在意義は「暗黙を明示にする」こと（第零原則）。
FEP の Precision Weighting は最も暗黙的なステップ。
**だからこそ HGK が明示化すべき操作。**

## 提案 (将来課題)

1. Hub WF に precision weight vector を導入
2. または新操作として Precision Weighting を定義
3. Attractor Engine の attract 度を定理レベルまで拡張

---

*Creator 対話から抽出。2026-02-08*
