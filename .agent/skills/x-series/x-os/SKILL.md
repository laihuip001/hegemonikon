---
id: "X-OS"
name: "Ousia → Schema"
category: "relation-layer"
pair: "O → S"
shared_coordinate: "C1 (Flow)"
relation_count: 8
type: "Anchor"
description: "本質 (Ousia) が設計 (Schema) を規定する8つの射"

activation_conditions:
  - context: "認識・探求・意志・行為の完了後、設計の問いが自然に生じるとき"
  - trigger: "「理解した。次はどう実装するか」の遷移"
  - confidence_threshold: 0.6
  - priority: "high"

triggers:
  - "認識結果を設計に変換"
  - "/noe >> /met"
  - "/bou >> /mek"
  - "本質→様態"
  - "理解→実装"

keywords: [ousia-schema, essence-to-design, x-os, understanding-to-implementation]
---

# X-OS: Ousia → Schema (本質→様態)

> **共有座標**: C1 (Flow)
> **型**: Anchor (Pure→Mixed)
> **認知的意味**: 理解したことを「どう実装するか」に落とす

## なぜこの接続が存在するか

人間の思考は「何か (What)」を理解した後、自然に「どうやって (How)」に遷移する。
O-series は認知の「What/Why」を担い、S-series は「How/When」の設計を担う。
この遷移は FEP の Inference→Action の micro-scale 表現。

## 8関係

| X | Source | Target | 認知的説明 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-OS1 | O1 Noēsis | S1 Metron | 本質理解→何をどのスケールで測るか | `/noe >> /met` |
| X-OS2 | O1 Noēsis | S2 Mekhanē | 本質理解→どの方法で実装するか | `/noe >> /mek` |
| X-OS3 | O2 Boulēsis | S1 Metron | 目的定義→目標の大きさを決める | `/bou >> /met` |
| X-OS4 | O2 Boulēsis | S2 Mekhanē | 目的定義→達成手段を設計する | `/bou >> /mek` |
| X-OS5 | O3 Zētēsis | S3 Stathmos | 問いの発見→評価基準を設定する | `/zet >> /sta` |
| X-OS6 | O3 Zētēsis | S4 Praxis | 問いの発見→探索方法を具体化する | `/zet >> /pra` |
| X-OS7 | O4 Energeia | S3 Stathmos | 行為の実行→成果基準を定義する | `/ene >> /sta` |
| X-OS8 | O4 Energeia | S4 Praxis | 行為の実行→次の実践を選択する | `/ene >> /pra` |

## 使用例

```ccl
# 本質理解 → 測定基準設計
/noe+{target: "FEP"} >> /met{scale: "micro"}

# 目的 → 方法選択
/bou+{goal: "96要素体系充実"} >> /mek+

# 問い → 実践
/zet+{open_question: true} >> /pra{concrete: true}
```

## アンチパターン

| ❌ やってはいけない | 理由 |
|:-------------------|:-----|
| 理解なしに設計に入る | O→S の因果が逆転。設計は認識に基づくべき |
| 全ての O を S に変換する | O1→S1, O2→S2 ... の機械的な対応は意味がない。文脈で選ぶ |
| S→O 方向で使う | 逆向き。設計から本質を導出するのは X-SO（未定義） |

## morphism_proposer 連携

`morphism_proposer.py` がこのペアを提案する条件:

```yaml
conditions:
  - current_series: "O"
  - after_completion: true
  - next_question_type: "implementation"
  - proposal: "X-OS: 認識結果を設計に変換しますか？"
```
