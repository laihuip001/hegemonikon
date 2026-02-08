---
# Theorem Metadata (v3.0)
id: "K2"
name: "Chronos"
greek: "Χρόνος"
series: "Kairos"
generation:
  formula: "Scale × Explore"
  result: "スケール探索 — 時間スケールの評価"

description: >
  どのくらいかかる？・時間軸を設定したい・期限と所要時間を評価したい時に発動。
  Time assessment, duration estimation, temporal scale setting.
  Use for: 時間, 期限, 所要時間, deadline, duration.
  NOT for: timing/opportunity (→ Eukairia K1).

triggers:
  - 時間の見積もり
  - 期限の設定
  - タイムスケールの評価
  - /chr コマンド

keywords: [chronos, time, duration, deadline, 時間, 期限]

related:
  upstream:
    - "P1 Khōra (X-PK2: 場の範囲→必要な時間軸)"
    - "P2 Hodos (X-PK4: 経路→この道にかかる時間)"
    - "S1 Metron (X-SK2: 測定基準→時間スケール)"
    - "S3 Stathmos (X-SK4: 評価基準→評価に必要な時間枠)"
    - "H2 Pistis (X-HK5: 確信→時間感覚支配 ⚠️)"
    - "H4 Doxa (X-HK7: 信念→時間感覚拡張/圧縮 ⚠️)"
  downstream:
    - "A1 Pathos (X-KA3: 時間圧→制約下の感情)"
    - "A2 Krisis (X-KA4: 時間圧→制約下の判断精度)"

version: "3.0.0"
workflow_ref: ".agent/workflows/chr.md"
risk_tier: L2
reversible: true
requires_approval: false
risks:
  - "確信/信念による時間感覚歪曲 (X-HK5, X-HK7)"
  - "楽観バイアスによる過小見積もり"
fallbacks: ["manual execution"]
---

# K2: Chronos (Χρόνος)

> **生成**: Scale × Explore
> **役割**: 時間スケールを評価する
> **認知的意味**: 「どのくらいかかるか」を正直に見積もる

## K1 Eukairia との区別

| | Eukairia (K1) | Chronos (K2) |
|:--|:-------------|:-------------|
| 問い | 「今やるべきか」 | 「どのくらいかかるか」 |
| 焦点 | タイミング (好機) | 時間量 (見積もり) |

## Processing Logic

```
入力: タスク / 目標
  ↓
[STEP 1] 時間スケールの設定
  ├─ ミクロ: 分〜時間
  ├─ メゾ: 日〜週
  └─ マクロ: 月〜年
  ↓
[STEP 2] バイアスチェック ⚠️
  ├─ X-HK5: 確信が時間感覚を支配していないか
  ├─ X-HK7: 信念が時間を圧縮/拡張していないか
  └─ 楽観バイアス: × 1.5 の安全マージン
  ↓
[STEP 3] 構造層からの入力確認
  ├─ X-PK2: 場のスケールと時間スケールは整合するか
  └─ X-SK2: 測定基準のスケールと時間スケールは整合するか
  ↓
出力: [時間見積もり, 安全マージン, バイアスチェック結果]
```

## X-series 接続

> K2 は6入力を受ける。うち2つはバイアスリスクあり。

### 入力射 (6本)

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-PK2 | P1 Khōra | 場の範囲→必要な時間軸 (構造層) | `/kho >> /chr` |
| X-PK4 | P2 Hodos | 経路→所要時間 (構造層) | `/hod >> /chr` |
| X-SK2 | S1 Metron | 測定基準→時間スケール (構造層) | `/met >> /chr` |
| X-SK4 | S3 Stathmos | 評価基準→評価時間枠 (構造層) | `/sta >> /chr` |
| X-HK5 ⚠️ | H2 Pistis | 確信→時間感覚支配 (反省層) | `/pis >> /chr` |
| X-HK7 ⚠️ | H4 Doxa | 信念→時間拡張/圧縮 (反省層) | `/dox >> /chr` |

### 出力射

| X | Target | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-KA3 | A1 Pathos | 時間圧→制約下の感情 | `/chr >> /pat` |
| X-KA4 | A2 Krisis | 時間圧→制約下の判断精度 | `/chr >> /dia` |

## CCL 使用例

```ccl
# 経路から所要時間を見積もり
/hod{route: "B→D→C"} >> /chr{estimate: true, margin: 1.5}

# バイアスチェック付き見積もり
/chr{task: "Phase D1"} _ /dia.epo{check: "optimism bias?"}

# 時間圧下の判断精度
/chr{deadline: "urgent"} >> /dia{mode: "time-constrained"}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 確信が高いから早く終わる | X-HK5 のバイアス。確信 ≠ 速度 |
| 安全マージンなし | 楽観バイアスは普遍的。×1.5 を基本とする |
| 時間圧で判断を雑にする | X-KA4: 時間圧→精度は「鋭くなる」べきで「雑になる」べきではない |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| estimate | `/chr.estimate` | 所要時間見積もり |
| deadline | `/chr.deadline` | 期限設定 |
| buffer | `/chr.buffer` | バッファ計算 |

---

*Chronos: 古代ギリシャにおける「時間」— 量的な時間 (cf. Kairos: 質的な時間)*
*v3.0: 6入力射バイアスチェック + Eukairia区別 (2026-02-07)*
