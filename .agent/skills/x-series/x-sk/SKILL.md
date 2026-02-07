---
id: "X-SK"
name: "Schema → Kairos"
category: "relation-layer"
pair: "S → K"
shared_coordinate: "C3 (Scale)"
relation_count: 8
type: "Bridge"
description: "設計 (Schema) が文脈 (Kairos) を制約する8つの射"

activation_conditions:
  - context: "設計の方法が決まった後、タイミングや目的の妥当性が問われるとき"
  - trigger: "「この方法で、いつ・なぜやるか」の遷移"
  - confidence_threshold: 0.5
  - priority: "medium"

triggers: ["設計→文脈制約", "/mek >> /tel", "/met >> /euk", "様態→文脈"]
keywords: [schema-kairos, design-to-context, x-sk]
---

# X-SK: Schema → Kairos (様態→文脈)

> **共有座標**: C3 (Scale) | **型**: Bridge (Mixed→Mixed)
> **認知的意味**: 設計の方法が好機と目的を制約する

## なぜこの接続が存在するか

選んだ方法は「いつやるか」「なぜやるか」を規定する。高精度の測定は時間がかかり (Metron→Chronos)、選んだ方法は目的整合性を要求する (Mekhanē→Telos)。Bridge 接続で意味的密度が高い。

## 8関係

| X | Source | Target | 認知的説明 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-SK1 | S1 Metron | K1 Eukairia | 測定基準→今が測定の好機か | `/met >> /euk` |
| X-SK2 | S1 Metron | K2 Chronos | 測定基準→時間軸のスケール感 | `/met >> /chr` |
| X-SK3 | S3 Stathmos | K1 Eukairia | 評価基準→今が評価の好機か | `/sta >> /euk` |
| X-SK4 | S3 Stathmos | K2 Chronos | 評価基準→評価に必要な時間枠 | `/sta >> /chr` |
| X-SK5 | S2 Mekhanē | K3 Telos | 方法→目的は正しいか | `/mek >> /tel` |
| X-SK6 | S2 Mekhanē | K4 Sophia | 方法→知恵は足りているか | `/mek >> /sop` |
| X-SK7 | S4 Praxis | K3 Telos | 実践→目的整合性 | `/pra >> /tel` |
| X-SK8 | S4 Praxis | K4 Sophia | 実践→知識の充足度 | `/pra >> /sop` |

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| タイミング無視で設計実行 | Eukairia (好機) の評価なしに動くのは reckless |
| 目的を後付けする | Telos が S の後に来るのは正しいが、S を正当化するためにTを変えてはいけない |
