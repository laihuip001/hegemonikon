---
id: "X-PK"
name: "Perigraphē → Kairos"
category: "relation-layer"
pair: "P → K"
shared_coordinate: "C3 (Scale)"
relation_count: 8
type: "Anchor"
description: "条件空間 (Perigraphē) が文脈 (Kairos) を制約する8つの射"

activation_conditions:
  - context: "領域・経路・軌道が定まった後、タイミングや目的の評価が必要なとき"
  - trigger: "「場は決まった。いつ・何のためにやるか」の遷移"
  - confidence_threshold: 0.6
  - priority: "high"

triggers: ["条件→文脈", "/kho >> /euk", "/tro >> /tel", "場→タイミング"]
keywords: [perigraphe-kairos, scope-to-timing, x-pk]
---

# X-PK: Perigraphē → Kairos (条件→文脈)

> **共有座標**: C3 (Scale) | **型**: Anchor (Pure→Mixed)
> **認知的意味**: 場の広さが「いつ・何のためか」を絞る

## なぜこの接続が存在するか

領域が定まれば時間と目的も自ずと定まる。狭い場なら短期、広い場なら長期。技法が決まれば学習目的が明確になる。条件空間はKairosを制約する自然なフィルター。

## 8関係

| X | Source | Target | 認知的説明 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-PK1 | P1 Khōra | K1 Eukairia | 場の範囲→行動すべき好機 | `/kho >> /euk` |
| X-PK2 | P1 Khōra | K2 Chronos | 場の範囲→必要な時間軸 | `/kho >> /chr` |
| X-PK3 | P2 Hodos | K1 Eukairia | 経路→今この道を進むべきか | `/hod >> /euk` |
| X-PK4 | P2 Hodos | K2 Chronos | 経路→この道にかかる時間 | `/hod >> /chr` |
| X-PK5 | P3 Trokhia | K3 Telos | サイクル→反復の目的は何か | `/tro >> /tel` |
| X-PK6 | P3 Trokhia | K4 Sophia | サイクル→反復に必要な知恵 | `/tro >> /sop` |
| X-PK7 | P4 Tekhnē | K3 Telos | 技法→目的整合性 | `/tek >> /tel` |
| X-PK8 | P4 Tekhnē | K4 Sophia | 技法→十分な知識があるか | `/tek >> /sop` |

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 場を定めずに好機を語る | Khōra なしの Eukairia は妄想 |
| 道を決めずに時間を見積もる | Hodos なしの Chronos は虚構 |
