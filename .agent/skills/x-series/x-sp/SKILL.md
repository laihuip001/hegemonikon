---
id: "X-SP"
name: "Schema → Perigraphē"
category: "relation-layer"
pair: "S → P"
shared_coordinate: "C3 (Scale)"
relation_count: 8
type: "Anchor"
description: "設計 (Schema) が条件空間 (Perigraphē) を規定する8つの射"

activation_conditions:
  - context: "設計の粒度が決まった後、適用範囲の問いが生じるとき"
  - trigger: "「設計した。どこまで適用するか」の遷移"
  - confidence_threshold: 0.6
  - priority: "high"

triggers: ["設計→適用範囲", "/met >> /kho", "/mek >> /tro", "様態→条件"]
keywords: [schema-perigraphe, design-to-scope, x-sp]
---

# X-SP: Schema → Perigraphē (様態→条件)

> **共有座標**: C3 (Scale) | **型**: Anchor (Mixed→Pure)
> **認知的意味**: 設計の粒度が適用範囲を決定する

## なぜこの接続が存在するか

測定基準を決めれば「どこで測るか」(場) が定まる。方法を選べば「どう巡回するか」(軌道) が定まる。設計のスケール感が条件空間を制約する。

## 8関係

| X | Source | Target | 認知的説明 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-SP1 | S1 Metron | P1 Khōra | 測定基準→適用領域を限定 | `/met >> /kho` |
| X-SP2 | S1 Metron | P2 Hodos | 測定基準→到達経路を制約 | `/met >> /hod` |
| X-SP3 | S3 Stathmos | P1 Khōra | 評価基準→評価対象の場を定める | `/sta >> /kho` |
| X-SP4 | S3 Stathmos | P2 Hodos | 評価基準→達成への道筋を絞る | `/sta >> /hod` |
| X-SP5 | S2 Mekhanē | P3 Trokhia | 方法→繰り返しサイクルを設計 | `/mek >> /tro` |
| X-SP6 | S2 Mekhanē | P4 Tekhnē | 方法→使う技法を選択 | `/mek >> /tek` |
| X-SP7 | S4 Praxis | P3 Trokhia | 実践→反復パターンを決める | `/pra >> /tro` |
| X-SP8 | S4 Praxis | P4 Tekhnē | 実践→必要な技法を選ぶ | `/pra >> /tek` |

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| スコープなしに設計を進める | P が S を制約するのではなく、S が P を規定する |
| 技法先行で方法を選ぶ | P4→S2 = 逆方向。手法ありきの設計は脆い |
