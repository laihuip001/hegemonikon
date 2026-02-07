---
id: "X-SP"
name: "Schema → Perigraphē"
category: "relation-layer"
pair: "S → P"
shared_coordinate: "C3 (Scale)"
relation_count: 8
type: "Anchor"
naturality: "構造"
zoom_chain: "設計のズーム → 適用のズーム"
description: "設計 (Schema) のズームレベルが条件空間 (Perigraphē) のズームレベルを規定する8つの射"

activation_conditions:
  - context: "設計の粒度が決まった後、適用範囲の問いが生じるとき"
  - trigger: "「この粒度で設計した。どのスケールで適用するか」"
  - confidence_threshold: 0.6
  - priority: "high"

triggers: ["設計→適用範囲", "/met >> /kho", "/mek >> /tro", "ズーム伝播"]
keywords: [schema-perigraphe, design-to-scope, x-sp, zoom-propagation]
---

# X-SP: Schema → Perigraphē (様態→条件)

> **共有座標**: C3 (Scale) | **型**: Anchor (Mixed→Pure) | **自然度**: 構造

## 認知的意味: ズームレベルの伝播

> **設計のズームレベルが適用のズームレベルを規定する。**

これは「自然に」起きる遷移ではなく、**意識的に操作する**もの。
設計者が粒度を決めると、その粒度が適用範囲を暗黙に制約する。
この制約に**気づかない**ことが多く、意識的な操作が必要。

### ズーム伝播の具体例

```
粒度「ミクロ」で設計 → 適用は「局所」に限定される
   /met{scale: micro} >> /kho{scope: local}

粒度「マクロ」で設計 → 適用は「広域」に展開される
   /met{scale: macro} >> /kho{scope: global}
```

**問題**: ズームのミスマッチ。マクロ設計をミクロ適用するとギャップが生じる。

## 8関係

| X | Source | Target | ズーム伝播 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-SP1 | S1 Metron | P1 Khōra | 測定のスケール → 適用領域のスケール | `/met >> /kho` |
| X-SP2 | S1 Metron | P2 Hodos | 測定のスケール → 到達経路のスケール | `/met >> /hod` |
| X-SP3 | S3 Stathmos | P1 Khōra | 評価のスケール → 評価対象のスケール | `/sta >> /kho` |
| X-SP4 | S3 Stathmos | P2 Hodos | 評価のスケール → 達成経路のスケール | `/sta >> /hod` |
| X-SP5 | S2 Mekhanē | P3 Trokhia | 方法の粒度 → 反復サイクルの粒度 | `/mek >> /tro` |
| X-SP6 | S2 Mekhanē | P4 Tekhnē | 方法の粒度 → 技法の粒度 | `/mek >> /tek` |
| X-SP7 | S4 Praxis | P3 Trokhia | 実践の粒度 → 反復パターンの粒度 | `/pra >> /tro` |
| X-SP8 | S4 Praxis | P4 Tekhnē | 実践の粒度 → 必要技法の粒度 | `/pra >> /tek` |

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| ズームミスマッチ | マクロ設計 + ミクロ適用 = ギャップ。スケールを揃える |
| 適用範囲から逆算して設計粒度を変える | P→S は逆方向。必要なら S を明示的に再設計する |
| ズーム伝播に気づかない | **構造層の最大リスク**。意識的にスケール一致を確認すべき |

## ズームチェーン上の位置

```
S (設計のズーム) → [X-SP] → P (適用のズーム) → [X-PK] → K (タイミングのズーム)
```

> このペアはズームチェーンの **第1段**。X-PK でタイミングに伝播する。
