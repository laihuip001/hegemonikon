# @review — 品質確認マクロ

> **Origin**: Forge v2.0 "✨ Quality?" + "🔧 Improve" モジュール
> **Category**: 反省マクロ (Reflect)
> **CCL**: `/dia+^ _ /pis _ I:[V[]>0.3]{C:{/dia _ /ene}} E:{/dox+}`

---

## 定義

```yaml
macro: @review
parameters:
  threshold: float (default: 0.3)
expansion: |
  /dia+^ _ /pis _ I:[V[]>$threshold]{C:{/dia _ /ene}} E:{/dox+}
```

---

## 処理フロー

```
Phase 1: /dia+^ (判断・深化・メタ上昇)
├─ 成果物を批評的にレビュー
├─ + = 深層まで精査
├─ ^ = メタ上昇。品質基準自体を問う
│   「何を基準に判断しているか」を検証
└─ 改善余地をスコアリング

Phase 2: /pis (確信度評価)
├─ レビュー結果に確信度を付与
├─ C (Confident) / U (Uncertain)
└─ 分散 V[] を計算

Phase 3: 分岐
├─ V[] > threshold (分散大)
│   → C:{/dia _ /ene} サイクルで判断→実行を品質安定まで繰り返す
└─ V[] ≤ threshold (品質OK)
    → /dox+ 確定記録（深化版）
```

---

## 演算子の意味

| 演算子 | 選択理由 |
|:-------|:---------|
| `^` (メタ上昇) | 品質基準自体を検証。表層で「良い」と判断しても基準が間違っている可能性 |
| `C:{}` (サイクル) | 品質が安定するまで判断→実行を繰り返す。1回の改善では不足かもしれない |
| `I:/E:` (条件分岐) | 分散値で改善要否を判定 |

---

## @review vs @v の違い

| | @review | @v (ccl-vet) |
|:--|:--------|:-------------|
| **問い** | 「これは良いものか」 | 「これは壊していないか」 |
| **入力** | 任意の成果物 | Git diff |
| **核心** | `/dia+^` (メタ判断) | `/kho{git_diff}` (空間差分) |
| **改善** | `C:{/dia_/ene}` (サイクル) | `C:{V:{/dia+}_/ene+}` (検証サイクル) |

---

## 使用例

```ccl
@review                    # 基本形
@build |> @review          # 構築 → 品質確認
C:{@review}                # 品質が安定するまでメタサイクル
@review ~ @fix             # 確認 ↔ 修正（振動）
```

---

*Forge Quality? + Improve → HGK CCL v2.0 (meta + cycle)*
