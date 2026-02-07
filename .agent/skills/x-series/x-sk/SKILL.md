---
id: "X-SK"
name: "Schema → Kairos"
category: "relation-layer"
pair: "S → K"
shared_coordinate: "C3 (Scale)"
relation_count: 8
type: "Bridge"
naturality: "構造"
zoom_chain: "設計のズーム → タイミングのズーム (X-SP + X-PK のショートカット)"
description: "設計 (Schema) のズームレベルが文脈 (Kairos) のズームレベルを直接規定する8つの射"

activation_conditions:
  - context: "設計の方法が決まった後、タイミングや目的のスケールが問われるとき"
  - trigger: "「この粒度で設計した。どのタイムスケールで実行するか」"
  - confidence_threshold: 0.5
  - priority: "medium"

triggers: ["設計→タイミング粒度", "/mek >> /tel", "/met >> /euk", "ズーム直接伝播"]
keywords: [schema-kairos, design-to-context, x-sk, zoom-propagation, shortcut]
---

# X-SK: Schema → Kairos (様態→文脈)

> **共有座標**: C3 (Scale) | **型**: Bridge (Mixed→Mixed) | **自然度**: 構造

## 認知的意味: ズームレベルの直接伝播

> **設計のズームレベルがタイミングのズームレベルを直接規定する。**

X-SP が S→P (設計→適用)、X-PK が P→K (適用→タイミング) のズーム伝播だとすると、
X-SK は **S→K の直接ショートカット**: 設計の粒度が「いつやるか」を飛ばして決定する。

### なぜショートカットが存在するか

Bridge 接続 (Mixed→Mixed) は意味的密度が最も高い。
設計のスケール感はタイミングのスケール感と**直接共鳴する**:

- 微細な設計 → 短期のタイミング感覚
- 壮大な設計 → 長期のタイミング感覚

## 8関係

| X | Source | Target | ズーム伝播 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-SK1 | S1 Metron | K1 Eukairia | 測定のスケール → 好機のスケール | `/met >> /euk` |
| X-SK2 | S1 Metron | K2 Chronos | 測定のスケール → 時間のスケール | `/met >> /chr` |
| X-SK3 | S3 Stathmos | K1 Eukairia | 評価のスケール → 好機のスケール | `/sta >> /euk` |
| X-SK4 | S3 Stathmos | K2 Chronos | 評価のスケール → 時間のスケール | `/sta >> /chr` |
| X-SK5 | S2 Mekhanē | K3 Telos | 方法の粒度 → 目的の粒度 | `/mek >> /tel` |
| X-SK6 | S2 Mekhanē | K4 Sophia | 方法の粒度 → 必要知恵の粒度 | `/mek >> /sop` |
| X-SK7 | S4 Praxis | K3 Telos | 実践の粒度 → 目的の粒度 | `/pra >> /tel` |
| X-SK8 | S4 Praxis | K4 Sophia | 実践の粒度 → 必要知恵の粒度 | `/pra >> /sop` |

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 微細な設計に壮大な目的を付ける | ズームミスマッチ。/tel のスケールが /mek のスケールと不整合 |
| ショートカットを常用する | P を飛ばすことでスコープ検証が抜ける。X-SP + X-PK を経由する方が安全 |
| 目的を後付けする | Telos が S の後に来るのは正しいが、S を正当化するために T を変えてはいけない |

## ズームチェーン上の位置

```
S (設計のズーム) ──[X-SK]──→ K (タイミングのズーム)
                    ↑ ショートカット
S → [X-SP] → P → [X-PK] → K  ← 正規ルート
```

> Bridge ならではの直接接続。ただし正規ルート (S→P→K) も常に存在する。
