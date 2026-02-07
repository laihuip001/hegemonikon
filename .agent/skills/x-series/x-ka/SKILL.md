---
id: "X-KA"
name: "Kairos → Akribeia"
category: "relation-layer"
pair: "K → A"
shared_coordinate: "C5 (Valence)"
relation_count: 8
type: "Anchor"
description: "文脈 (Kairos) が精密判断 (Akribeia) を確定させる8つの射"

activation_conditions:
  - context: "タイミング・目的・知恵が明確になった後、精密な判断が求められるとき"
  - trigger: "「文脈はわかった。では精密にどう判定するか」の遷移"
  - confidence_threshold: 0.7
  - priority: "high"

triggers: ["文脈→精密", "/euk >> /dia", "/tel >> /gno", "/sop >> /epi", "文脈→判断"]
keywords: [kairos-akribeia, context-to-precision, x-ka, timing-to-judgment]
---

# X-KA: Kairos → Akribeia (文脈→精密)

> **共有座標**: C5 (Valence) | **型**: Anchor (Mixed→Pure)
> **認知的意味**: 文脈の制約が精度要求を確定させる

## なぜこの接続が存在するか

締切があれば判断が鋭くなる (Chronos→Krisis)。目的が明確なら必要な知識も確定する (Telos→Epistēmē)。文脈が Akribeia の要求水準を自然に設定する。A-series は体系の「最終出力」であり、K→A は情報の最終精錬。

## 8関係

| X | Source | Target | 認知的説明 | CCL |
|:--|:-------|:-------|:-----------|:----|
| X-KA1 | K1 Eukairia | A1 Pathos | 好機→機会への感情的反応 | `/euk >> /pat` |
| X-KA2 | K1 Eukairia | A2 Krisis | 好機→今行動すべきかの判定 | `/euk >> /dia` |
| X-KA3 | K2 Chronos | A1 Pathos | 時間圧→時間制約下の感情 | `/chr >> /pat` |
| X-KA4 | K2 Chronos | A2 Krisis | 時間圧→時間制約下の判断精度 | `/chr >> /dia` |
| X-KA5 | K3 Telos | A3 Gnōmē | 目的→目的から原則を演繹 | `/tel >> /gno` |
| X-KA6 | K3 Telos | A4 Epistēmē | 目的→必要な知識の確定 | `/tel >> /epi` |
| X-KA7 | K4 Sophia | A3 Gnōmē | 知恵→知恵から格言を抽出 | `/sop >> /gno` |
| X-KA8 | K4 Sophia | A4 Epistēmē | 知恵→知恵を体系的知識に昇格 | `/sop >> /epi` |

## 使用例

```ccl
# 好機判断 → 批判的レビュー
/euk{opportunity: "detected"} >> /dia+{verify: "is_real?"}

# 知恵 → 知識昇格
/sop{research: "FEP papers"} >> /epi{formalize: true}

# 目的 → 原則抽出
/tel{purpose: "96体系充実"} >> /gno{extract: "lessons_learned"}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 文脈不明のまま精密判断する | K→A の因果を飛ばしている。「何のために判断するか」が先 |
| 時間圧で判断を雑にする | Chronos→Krisis の適切な使い方は「制約下で鋭くなる」こと。雑になるのは逆 |
| 知恵を知識と混同する | Sophia ≠ Epistēmē。知恵は文脈依存、知識は文脈独立 |
