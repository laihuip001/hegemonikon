# @review — 品質確認マクロ

> **Origin**: Forge v2.0 "✨ Quality?" + "🔧 Improve" モジュール
> **Category**: 反省マクロ (Reflect)
> **CCL**: `/dia+ _ /pis _ I:[V[]>0.3]{/ene{improve}} E:{/dox+}`

---

## 定義

```yaml
macro: @review
parameters:
  threshold: float (default: 0.3)
expansion: |
  /dia+ _ /pis _ I:[V[]>$threshold]{/ene{improve}} E:{/dox+}
```

---

## 処理フロー

```
Phase 1: /dia+ (判断・深化)
├─ 成果物を批評的にレビュー
├─ 品質基準との差分を列挙
└─ 改善余地をスコアリング

Phase 2: /pis (確信度評価)
├─ レビュー結果に確信度を付与
├─ C (Confident) / U (Uncertain)
└─ 分散 V[] を計算

Phase 3: 分岐
├─ V[] > threshold (分散大) → /ene{improve} 改善実行
└─ V[] ≤ threshold (品質OK) → /dox+ 確定記録
```

---

## 使用例

```ccl
@review                    # 基本形
@build |> @review          # 構築 → 品質確認
C:{@review}                # 品質が安定するまでサイクル
@review ~ @fix             # 確認 ↔ 修正（振動）
```

---

*Forge Quality? + Improve → HGK CCL v1.0*
