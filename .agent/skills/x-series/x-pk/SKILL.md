---
id: "X-PK"
name: "Perigraphē → Kairos"
category: "relation-layer"
pair: "P → K"
shared_coordinate: "C3 (Scale)"
relation_count: 8
type: "Anchor"
naturality: "構造"
zoom_chain: "適用のズーム → タイミングのズーム (チェーン第2段)"
description: "条件空間 (Perigraphē) のズームレベルが文脈 (Kairos) のズームレベルを規定する8つの射"

activation_conditions:
  - context: "領域・経路・軌道が定まった後、タイミングや目的のスケール評価が必要なとき"
  - trigger: "「このスケールの場を設定した。どのタイムスケールで動くか」"
  - confidence_threshold: 0.6
  - priority: "high"

triggers: ["適用→タイミング粒度", "/kho >> /euk", "/tro >> /tel", "ズームチェーン第2段"]
keywords: [perigraphe-kairos, scope-to-timing, x-pk, zoom-propagation, chain-stage-2]
---

# X-PK: Perigraphē → Kairos (条件→文脈)

> **共有座標**: C3 (Scale) | **型**: Anchor (Pure→Mixed) | **自然度**: 構造

## 認知的意味: ズームチェーンの第2段

> **適用のズームレベルがタイミングのズームレベルを規定する。**

ズームチェーンの完全形: `S → [X-SP] → P → [X-PK] → K`

X-SP で設計ズームが適用ズームになり、X-PK で適用ズームがタイミングズームになる。
場の広さ (Khōra) は「どのタイムフレームで考えるか」(Chronos) を自然に決定する。

### ズーム伝播の完全例

```
S: /met{scale: sprint}          # 設計: スプリント単位
   → [X-SP] →
P: /kho{scope: 1_week}          # 適用: 1週間の範囲
   → [X-PK] →
K: /chr{timeframe: 1_week}      # タイミング: 1週間サイクル
   /euk{check: "今週中に好機あり?"}
```

## 8関係

| X | Source | Target | ズーム伝播 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-PK1 | P1 Khōra | K1 Eukairia | 場のスケール → 好機のスケール | `/kho >> /euk` |
| X-PK2 | P1 Khōra | K2 Chronos | 場のスケール → 時間のスケール | `/kho >> /chr` |
| X-PK3 | P2 Hodos | K1 Eukairia | 経路のスケール → 好機のスケール | `/hod >> /euk` |
| X-PK4 | P2 Hodos | K2 Chronos | 経路のスケール → 時間のスケール | `/hod >> /chr` |
| X-PK5 | P3 Trokhia | K3 Telos | 軌道のスケール → 目的のスケール | `/tro >> /tel` |
| X-PK6 | P3 Trokhia | K4 Sophia | 軌道のスケール → 知恵のスケール | `/tro >> /sop` |
| X-PK7 | P4 Tekhnē | K3 Telos | 技法のスケール → 目的のスケール | `/tek >> /tel` |
| X-PK8 | P4 Tekhnē | K4 Sophia | 技法のスケール → 知恵のスケール | `/tek >> /sop` |

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 場を定めずに好機を語る | Khōra なしの Eukairia は妄想。ズームの起点がない |
| 道を決めずに時間を見積もる | Hodos なしの Chronos は虚構。距離なき時間は無意味 |
| ズーム伝播を無視して P と K を独立に設定 | S→P→K のチェーンを断ち切るとスケール不整合が生じる |

## ズームチェーン全体図

```
S (設計)     P (適用)     K (タイミング)
  ├─[X-SP]──→  ├─[X-PK]──→  │
  │            │ ← 今ここ   │
  └─[X-SK]───────────────→  │ (ショートカット)
```

> X-PK はチェーン第2段。X-SP の出力を受けて K に伝播する。
> X-SK はこのチェーンのショートカット (Bridge)。
