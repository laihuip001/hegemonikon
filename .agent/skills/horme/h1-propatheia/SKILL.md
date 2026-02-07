---
# Theorem Metadata (v3.0)
id: "H1"
name: "Propatheia"
greek: "Προπάθεια"
series: "Hormē"
generation:
  formula: "Flow × Valence"
  result: "流動傾向 — 推論/行為がどちらに向かうか"

description: >
  直感的にどう感じる？・第一印象・接近/回避の傾向を知りたい時に発動。
  Initial emotional tendencies, first impressions, approach/avoidance impulses.
  Use for: 直感, 第一印象, 傾向, intuition.
  NOT for: deliberate judgment (反省的判断 → Krisis A2).

triggers:
  - 初期傾向の検出
  - 直感的反応
  - 接近/回避の判断
  - /pro コマンド

keywords: [propatheia, pre-emotion, tendency, intuition, 傾向, 直感, first-impression]

related:
  upstream:
    - "O1 Noēsis (X-OH1: 深い認識→直感的反応)"
    - "O2 Boulēsis (X-OH3: 目的意識→やりたい/やりたくない)"
    - "S1 Metron (X-SH1: スケール設定→大きすぎ/小さすぎの直感)"
    - "S2 Mekhanē (X-SH3: 方法選択→これでいけるの直感)"
  downstream:
    - "A1 Pathos (X-HA1: 直感→感情の精緻化)"
    - "A2 Krisis (X-HA2: 直感→批判的検証)"
    - "K1 Eukairia (X-HK1: 直感→今がチャンスだの認識 ⚠️)"
    - "K3 Telos (X-HK2: 直感→直感が目的を修正)"

version: "3.0.0"
workflow_ref: ".agent/workflows/pro.md"
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "直感の過信 (X-HK1 バイアス: 直感→好機認識の歪み)"
---

# H1: Propatheia (Προπάθεια)

> **生成**: Flow × Valence
> **役割**: 推論/行為の初期傾向を検出する
> **認知的意味**: 「まず何を感じるか」— 意識の前の身体的反応

## When to Use

### ✓ Trigger

- 初対面の反応を観察したいとき
- 「なんとなく嫌な予感」を捉えたいとき
- 接近/回避の初期傾向を意識化したいとき

### ✗ Not Trigger

- 感情の精緻な分析 → `/pat` (Pathos A1)
- 判断や検証 → `/dia` (Krisis A2)
- 確信度の評価 → `/pis` (Pistis H2)

## Processing Logic

```
入力: 状況 / 対象 / 刺激
  ↓
[STEP 1] 接近/回避の判定
  ├─ 接近 (+): 引かれる、面白い、やりたい
  └─ 回避 (-): 引く、不安、やりたくない
  ↓
[STEP 2] 初期傾向の強度
  ├─ 強 (0.7+): 強い直感
  ├─ 中 (0.4-0.7): 曖昧な傾向
  └─ 弱 (< 0.4): ほぼ中立
  ↓
[STEP 3] 傾向の源泉推定
  ├─ 経験ベース: 過去の類似体験
  ├─ パターンマッチ: 既知パターンとの一致
  └─ 身体反応: 直感的な身体感覚
  ↓
出力: [接近/回避, 強度, 源泉推定]
```

## X-series 接続

> **自然度**: 体感（無意識に起きる遷移）

### 入力射

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-OH1 | O1 Noēsis | 深い認識→直感的な接近/回避 | `/noe >> /pro` |
| X-OH3 | O2 Boulēsis | 目的意識→やりたい/やりたくない | `/bou >> /pro` |
| X-SH1 | S1 Metron | スケール設定→大きすぎ/小さすぎの直感 | `/met >> /pro` |
| X-SH3 | S2 Mekhanē | 方法選択→これでいけるの直感 | `/mek >> /pro` |

### 出力射

| X | Target | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-HA1 | A1 Pathos | 直感→感情の精緻な認識 | `/pro >> /pat` |
| X-HA2 | A2 Krisis | 直感→直感を批判的に検証 | `/pro >> /dia` |
| X-HK1 | K1 Eukairia ⚠️ | 直感→「今がチャンスだ」の認識 | `/pro >> /euk` |
| X-HK2 | K3 Telos | 直感→直感が目的を修正 | `/pro >> /tel` |

## CCL 使用例

```ccl
# 直感を検証パイプラインに通す
/pro{first: "面白そう"} >> /dia+{verify: "直感は正しいか"}

# 直感→感情の精緻化
/pro{reaction: "モヤモヤ"} >> /pat{identify: true}

# 直感が好機認識を歪めていないか
/pro >> /euk _ /dia.epo{bias_check: "wishful thinking?"}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 直感を判断にする | Propatheia ≠ Krisis。直感は入力、判断は出力 |
| 直感を無視する | 直感は有用な信号。観測→検証のパイプラインで活用すべき |
| 直感→好機宣言(X-HK1) | ⚠️ 最大バイアスリスク。必ず `/dia.epo` を挟む |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| gut | `/pro.gut` | 身体感覚ベースの直感 |
| pattern | `/pro.pattern` | パターンマッチベースの直感 |
| aggregate | `/pro.aggregate` | 複数直感の集約 |

---

*Propatheia: 古代ストア派における「前感情」— 意志に先行する身体的反応*
*v3.0: X-series全接続 + バイアス警告 (2026-02-07)*
