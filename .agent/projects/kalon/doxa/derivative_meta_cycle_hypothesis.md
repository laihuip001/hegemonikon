---
title: "派生メタサイクル仮説 — 妥当性と反証可能性の検証"
created: "2026-02-08T08:49:00+09:00"
updated: "2026-02-08T10:02:00+09:00"
source: "/dia+~*/noe → /noe~*/dia"
confidence: 
  H0_weak: 0.75
  H1_mid: 0.60
  H1_strong: 0.40
  H2_proof: 0.20
related: 
  - kernel/taxis.md
  - .agent/projects/kalon/doxa/x_series_naturality_layers.md
tags: [fep, meta-cycle, derivatives, category-theory, falsifiable]
---

## 仮説体系

| ID | 主張 | 確信度 |
|:---|:-----|:------:|
| H₀ | 24派生は4メタパターンに分類できる | **0.75** |
| H₁中 | 4パターンはFEPサイクルに対応する | **0.60** |
| H₁強 | 座標×FEP×圏論は構造的同型 | **0.40** |
| H₂ | 96体系の必然性の証明 | **0.20** |

## 4メタパターンとFEP対応 (再配列版)

初回配列の Scale↔PredError は誤り。検証により以下に修正:

| 座標 | FEP | メタパターン | 圏論(比喩) | 確信度 |
|:-----|:----|:-----------|:-----------|:------:|
| Internality | Prediction | コミット | (Colimit) | 0.45 |
| **Function** | **Prediction Error** | **バイアスチェック** | (Pullback) | 0.60 |
| **Scale** | **Model Update** | **構造分解** | (Pushout) | **0.75** |
| Precision | Precision Weight | 深層/表層分離 | (Fiber) | 0.60* |

\* Precision ペアは循環的（同語彙使用のため独立証拠にならない）

## 反証可能性テスト

Precision-PrecWeight は固定（同語反復）。残り3座標×3FEPステップ = 3! = 6通り。

| 配列 | 妥当ペア | 判定 |
|:-----|:--------:|:----:|
| 再配列版 (正) | 3/3 | ✅ |
| 初回版 | 2/3 | ⚠️ |
| ランダムR1 | 1/3 | ❌ |
| ランダムR2 | 1/3 | ❌ |

結果: **6通り中2通り妥当 (33%)**。偶然 (17%) より高いが必然 (100%) ではない。

→ 仮説は「空虚ではないが、必然でもない」

## 消化の不変量 (H₀ の核)

```
思考法の圏 C ──η (/eat)──→ Hegemonikón H ──Forget──→ FEP F
```

- **保存**: 4メタパターン (消化の不変量)
- **失われ**: 各思考法の「手触り」(射ηの固有形状)
- **手触りの例**: Five Whysの忍耐、Premortinの胆力、Design Thinkingの身体性

## 判断

- 「FEP が正しい」の証拠ではない（実証が必要）
- 「FEP が美しい」の証拠である（多様性の中の統一）
- 圏論対応は**比喩**。universality条件が未定義の時点で厳密な同型ではない
- 最も堅い発見は **Scale-ModelUpdate-Pushout** 対応 (0.75)

## 未検証

- [ ] 4ではなく3や5パターンでも同等の分類が可能かの検証
- [ ] 圏論 universality に対応する認知的操作の定義
- [ ] 独立データセットでの追試（別の思考法群を消化して同じ4パターンが出るか）
- [x] ~~ランダム配列テスト~~ → 6通り中2通り(33%)
- [x] ~~循環性チェック~~ → Precisionペアは循環的

---

*Phase C1 /dia+~*/noe → /noe~*/dia で2回検証。2026-02-08*
