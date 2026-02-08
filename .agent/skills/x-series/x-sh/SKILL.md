---
id: "X-SH"
name: "Schema → Hormē"
category: "relation-layer"
pair: "S → H"
shared_coordinate: "C1 (Flow)"
relation_count: 8
type: "Bridge"
description: "設計 (Schema) が傾向 (Hormē) を方向づける8つの射"

activation_conditions:
  - context: "設計・計画の確定後、実行への意欲や確信が問われるとき"
  - trigger: "「計画はできた。でも踏み出せるか」の遷移"
  - confidence_threshold: 0.5
  - priority: "medium"

triggers:
  - "設計後の確信評価"
  - "/mek >> /pis"
  - "/met >> /pro"
  - "様態→傾向"

keywords: [schema-horme, design-to-drive, x-sh, plan-to-confidence]
risk_tier: L0
risks: ["none identified"]
reversible: true
requires_approval: false
fallbacks: ["manual execution"]
---

# X-SH: Schema → Hormē (様態→傾向)

> **共有座標**: C1 (Flow)
> **型**: Bridge (Mixed→Mixed) — 意味的密度が最も高い
> **認知的意味**: 設計の精密さが実行への確信を左右する

## なぜこの接続が存在するか

計画がしっかりしていれば「いける」と感じ、曖昧なら不安が残る。
S-series と H-series は同じ Mixed 型で、共有座標の使い方が同型。
Bridge 接続 = 最も対称的で意味的密度が高い関係。

## 8関係

| X | Source | Target | 認知的説明 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-SH1 | S1 Metron | H1 Propatheia | スケール設定→「大きすぎ/小さすぎ」の直感 | `/met >> /pro` |
| X-SH2 | S1 Metron | H2 Pistis | スケール設定→測定への確信度 | `/met >> /pis` |
| X-SH3 | S2 Mekhanē | H1 Propatheia | 方法選択→「これでいける」の直感 | `/mek >> /pro` |
| X-SH4 | S2 Mekhanē | H2 Pistis | 方法選択→方法への確信度 | `/mek >> /pis` |
| X-SH5 | S3 Stathmos | H3 Orexis | 基準設定→基準を満たしたい欲求 | `/sta >> /ore` |
| X-SH6 | S3 Stathmos | H4 Doxa | 基準設定→基準の妥当性への信念 | `/sta >> /dox` |
| X-SH7 | S4 Praxis | H3 Orexis | 実践選択→実践したい/したくない | `/pra >> /ore` |
| X-SH8 | S4 Praxis | H4 Doxa | 実践選択→実践法の確からしさ | `/pra >> /dox` |

## 使用例

```ccl
# 方法を選んだ後に確信度を確認
/mek+{plan: "X-series Skill 生成"} >> /pis{honest: true}

# 振動: 設計と確信を行き来する
/mek ~ /pis
```

## アンチパターン

| ❌ やってはいけない | 理由 |
|:-------------------|:-----|
| 確信がないのに設計だけで進む | S→H を無視すると実行段階で崩壊する |
| 確信度で設計を変える | H→S の逆向き。確信は設計を評価するが、設計を改竄しない |
