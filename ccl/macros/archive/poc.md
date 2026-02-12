# @poc — プロトタイプマクロ

> **Origin**: Forge v2.0 "🧪 Prototype" モジュール
> **Category**: 行為マクロ (Act/Create)
> **CCL**: `/zet- |> /ene _ V:{/dia-{out: pass|fail}}`

---

## 定義

```yaml
macro: @poc
parameters: []
expansion: |
  /zet- |> /ene _ V:{/dia-{out: pass|fail}}
```

---

## 処理フロー

```
Phase 1: /zet- (探求・縮約)
├─ 問いを1つに絞る
├─ 「何を検証するか」だけ決める
└─ - = 完成度の意図的制限。雑でいいから速く

  |> (単一の検証仮説が行為の入力に)

Phase 2: /ene (行為・素のまま)
├─ 修飾子なし = 考えすぎず、削りすぎず、ただ動く
├─ 試作品を最速で作る
└─ 検証可能な状態にするだけ

Phase 3: V:{/dia-{out: pass|fail}} (検証 → 判断・縮約・型制約)
├─ 試作品が仮説を検証できるか判定
├─ - = 品質は問わない。仮説の成否のみ
├─ {out: pass|fail} = 二値判定。品質の入り込む余地を排除
└─ pass → 本構築へ、fail → 仮説修正
```

---

## 演算子の意味

| 演算子 | 選択理由 |
|:-------|:---------|
| `-` (縮約) | `/zet-` = 問いを1つに絞る。Prototype = 最小限 |
| 素 (修飾子なし) | `/ene` = 考えすぎずただ動く。プロトタイプの精神 |
| `V:{}` (検証) | 検証ゲート |
| `{out: pass\|fail}` (型) | 品質判断を排除。仮説の成否のみ |

---

## 使用例

```ccl
@poc                       # 基本形
@poc |> @build             # 試作 → 本構築
F:[×3]{@poc} |> /bou       # 3つ試作 → 最良を選定
@poc ~ @devil              # 試作 ↔ 攻撃（改善ループ）
```

---

*Forge Prototype → HGK CCL v2.0 (typed verification)*
