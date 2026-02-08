---
# Theorem Metadata (v3.0)
id: "K1"
name: "Eukairia"
greek: "Εὐκαιρία"
series: "Kairos"
generation:
  formula: "Scale × Valence"
  result: "スケール傾向 — 好機の認識"

description: >
  今がチャンスか？・タイミングは正しいか？・好機の判定時に発動。
  Opportunity recognition, timing assessment, kairos moment detection.
  Use for: 好機, タイミング, 今か, opportunity.
  NOT for: 時間の見積もり (→ Chronos K2).

triggers:
  - 好機の判定
  - タイミング評価
  - 「今やるべきか」の問い
  - /euk コマンド

keywords: [eukairia, opportunity, timing, moment, kairos, 好機, タイミング]

related:
  upstream:
    - "P1 Khōra (X-PK1: 場の範囲→行動すべき好機)"
    - "P2 Hodos (X-PK3: 経路→今この道を進むべきか)"
    - "H1 Propatheia (X-HK1: 直感→今がチャンスだの認識 ⚠️)"
    - "H3 Orexis (X-HK3: 欲求→欲しいものに好機を見出す ⚠️)"
    - "S1 Metron (X-SK1: 測定基準→今が測定の好機か)"
    - "S3 Stathmos (X-SK3: 評価基準→今が評価の好機か)"
  downstream:
    - "A1 Pathos (X-KA1: 好機→機会への感情的反応)"
    - "A2 Krisis (X-KA2: 好機→今行動すべきかの批判的判定)"

version: "3.0.0"
workflow_ref: ".agent/workflows/euk.md"
risk_tier: L2
reversible: true
requires_approval: false
risks:
  - "直感/欲求による好機バイアス (X-HK1, X-HK3)"
  - "好機の見逃し (false negative)"
fallbacks: ["manual execution"]
---

# K1: Eukairia (Εὐκαιρία)

> **生成**: Scale × Valence
> **役割**: 好機を認識する — 「今がそのときか」
> **認知的意味**: タイミングの判定。行動すべき瞬間を見極める

## When to Use

### ✓ Trigger

- 「今やるべきか」が問われるとき
- 好機の有無を判定したいとき
- 行動のタイミングを最適化したいとき

### ✗ Not Trigger

- 時間の見積もり → `/chr` (Chronos)
- 目的の確認 → `/tel` (Telos)

## Processing Logic

```
入力: 状況 / 行動候補
  ↓
[STEP 1] 好機シグナルの検出
  ├─ 外部要因: 環境の変化、窓の開閉
  ├─ 内部要因: 準備度、エネルギー状態
  └─ 関係要因: 他者の状態、協調可能性
  ↓
[STEP 2] バイアスチェック ⚠️
  ├─ X-HK1: 直感バイアス → 「本当にチャンスか」
  ├─ X-HK3: 欲求バイアス → 「欲しいから好機に見えていないか」
  └─ 確信度との交差 → 確信が高いだけでは好機ではない
  ↓
[STEP 3] 好機判定
  ├─ GO: 十分な根拠あり
  ├─ WAIT: 条件不足
  └─ PASS: この機会は見送り
  ↓
出力: [GO/WAIT/PASS, 根拠, バイアスチェック結果]
```

## X-series 接続

> **自然度**: 反省（注意を向ければ気づく遷移）

### 入力射 (6本 — K1 は多くの入力を受ける)

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-PK1 | P1 Khōra | 場の範囲→好機 (構造層ズーム) | `/kho >> /euk` |
| X-PK3 | P2 Hodos | 経路→今この道を進むべきか (構造層) | `/hod >> /euk` |
| X-HK1 ⚠️ | H1 Propatheia | 直感→「今がチャンスだ」(バイアスリスク) | `/pro >> /euk` |
| X-HK3 ⚠️ | H3 Orexis | 欲求→好機を見出す (バイアスリスク) | `/ore >> /euk` |
| X-SK1 | S1 Metron | 測定基準→今が測定の好機か (構造層) | `/met >> /euk` |
| X-SK3 | S3 Stathmos | 評価基準→今が評価の好機か (構造層) | `/sta >> /euk` |

### 出力射

| X | Target | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-KA1 | A1 Pathos | 好機→機会への感情的反応 | `/euk >> /pat` |
| X-KA2 | A2 Krisis | 好機→今行動すべきかの批判的判定 | `/euk >> /dia` |

## CCL 使用例

```ccl
# 好機判定 → 批判的検証
/euk{signal: "detected"} >> /dia+{verify: "本当に好機か"}

# バイアスチェック付き好機判定
/euk _ /dia.epo{bias: ["X-HK1", "X-HK3"]}

# ズームチェーンによる好機判定
/kho{scope: "defined"} >> /euk{from: "structural"}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 欲求ベースの好機宣言 | X-HK3 バイアス。構造層 (X-PK) からの入力を優先すべき |
| 全て GO にする | 好機でないときに WAIT/PASS する勇気が必要 |
| バイアスチェックをスキップ | STEP 2 は必須。K1 は多くのバイアス入力を受ける |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| signal | `/euk.signal` | シグナル検出のみ |
| verify | `/euk.verify` | バイアスチェック付き判定 |
| window | `/euk.window` | 好機の窓の開閉予測 |

---

*Eukairia: 古代ギリシャにおける「好機・良いタイミング」(eu + kairos)*
*v3.0: 6入力射のバイアスチェック統合 (2026-02-07)*
