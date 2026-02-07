---
# Theorem Metadata (v2.1)
id: "H2"
name: "Pistis"
greek: "Πίστις"
series: "Hormē"
generation:
  formula: "Flow × Precision"
  result: "流動確信 — 推論/行為の確信度"

description: >
  どのくらい確か？・確信度を評価したい・信頼できる？時に発動。
  Confidence assessment, trust evaluation, certainty in current approach.
  Use for: 確信, 信頼, certainty, どのくらい確か.
  NOT for: confidence already clear (proceed directly).

triggers:
  - 確信度の評価
  - 信頼性判断
  - 推論の確度チェック

keywords:
  - pistis
  - confidence
  - trust
  - belief
  - certainty
  - 確信
  - 信頼

related:
  upstream:
    - "S2 Mekhanē"
  downstream:
    - "A2 Krisis"
  x_series:
    - "← X-SH2 ← S2 Mekhanē"
    - "X-HA2 → A2 Krisis"

implementation:
  micro: "(implicit in /chk)"
  macro: "(future)"
  templates: []

version: "2.1.0"
workflow_ref: ".agent/workflows/pis.md"
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "動機評価の偏りによる行動指針の歪み"
fallbacks: []
---

# H2: Pistis (Πίστις)

> **生成**: Flow × Precision
> **役割**: 推論/行為の確信度

## When to Use

### ✓ Trigger

- 確信度の評価
- 現在のアプローチへの信頼性判断
- 不確実性のチェック (U スコア)

### ✗ Not Trigger

- 確信度が既に明確

## Processing Logic

```
入力: 推論/行為
  ↓
[STEP 1] 確信度評価
  ├─ C (Certain): 高確信
  └─ U (Uncertain): 低確信
  ↓
[STEP 2] 確信度スコア算出 (0-1)
  ↓
出力: 確信度スコア + 根拠
```

## X-series 接続

```mermaid
graph LR
    S2[S2 Mekhanē] -->|X-SH2| H2[H2 Pistis]
    H2 -->|X-HA2| A2[A2 Krisis]
```

---

*Pistis: 古代ギリシャにおける「信頼・確信・信仰」*

---

## Related Modes

このスキルに関連する `/pis` WFモード (7件):

| Mode | CCL | 用途 |
|:-----|:----|:-----|
| subj | `/pis.subj` | 主観的確信 |
| inte | `/pis.inte` | 統合確信 |
| obje | `/pis.obje` | 客観的確信 |
| calibrate | `/pis.calibrate` | 較正 |
| bayes | `/pis.bayes` | ベイズ更新 |
| probabilistic | `/pis.probabilistic` | 確率的 |
| uncertainty | `/pis.uncertainty` | 不確実性 |
