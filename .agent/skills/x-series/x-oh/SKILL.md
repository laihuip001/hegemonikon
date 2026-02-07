---
id: "X-OH"
name: "Ousia → Hormē"
category: "relation-layer"
pair: "O → H"
shared_coordinate: "C1 (Flow)"
relation_count: 8
type: "Anchor"
description: "本質 (Ousia) が傾向 (Hormē) を生む8つの射"

activation_conditions:
  - context: "認識・意志の完了後、感情的反応や確信が自然に生じるとき"
  - trigger: "「理解して、自分がどう感じるか気づいた」の遷移"
  - confidence_threshold: 0.5
  - priority: "medium"

triggers:
  - "認識の後に感情反応"
  - "/noe >> /pro"
  - "/bou >> /pis"
  - "本質→傾向"
  - "理解→欲求"

keywords: [ousia-horme, essence-to-drive, x-oh, understanding-to-motivation]
---

# X-OH: Ousia → Hormē (本質→傾向)

> **共有座標**: C1 (Flow)
> **型**: Anchor (Pure→Mixed)
> **認知的意味**: 理解したことが「何を欲するか」を変える

## なぜこの接続が存在するか

理解は欲求を変える。本質を知れば「これが欲しい」が生まれ、
目的を定めれば確信が形成される。認識の深さが動機の方向を決定する。
FEP 的には、予測モデルの精緻化が precision（確信度）を変化させる。

## 8関係

| X | Source | Target | 認知的説明 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-OH1 | O1 Noēsis | H1 Propatheia | 深い認識→直感的な接近/回避反応 | `/noe >> /pro` |
| X-OH2 | O1 Noēsis | H2 Pistis | 深い認識→理解に対する確信度 | `/noe >> /pis` |
| X-OH3 | O2 Boulēsis | H1 Propatheia | 目的意識→やりたい/やりたくない | `/bou >> /pro` |
| X-OH4 | O2 Boulēsis | H2 Pistis | 目的意識→意志の確からしさ | `/bou >> /pis` |
| X-OH5 | O3 Zētēsis | H3 Orexis | 問いの探求→「これが欲しい」の発生 | `/zet >> /ore` |
| X-OH6 | O3 Zētēsis | H4 Doxa | 問いの探求→暫定的信念の形成 | `/zet >> /dox` |
| X-OH7 | O4 Energeia | H3 Orexis | 行為の完了→次に何を望むか | `/ene >> /ore` |
| X-OH8 | O4 Energeia | H4 Doxa | 行為の完了→経験が信念になる | `/ene >> /dox` |

## 使用例

```ccl
# 認識の後に確信度を評価
/noe+{target: "新技術"} >> /pis{evaluate: true}

# 行為の後に信念を記録
/ene{task: "completed"} >> /dox{persist: true}
```

## アンチパターン

| ❌ やってはいけない | 理由 |
|:-------------------|:-----|
| 感情先行で認識をスキップ | H→O の逆向き。直感は認識の後に検証すべき |
| 全ての認識を感情に変換する | O1→H1 は自然だが強制すべきではない |
| 確信度を操作する | Pistis は観測するもの。意図的に上げ下げしない |
