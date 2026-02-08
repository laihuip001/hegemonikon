---
# Theorem Metadata (v3.0)
id: "S1"
name: "Metron"
greek: "Μέτρον"
series: "Schema"
generation:
  formula: "Internality × Scale"
  result: "内在スケール — 測定基準・粒度の決定"

description: >
  どのスケールで？・粒度を決めたい・測定基準を設定したい時に発動。
  Scale determination, measurement criteria, granularity setting.
  Use for: スケール, 粒度, 測定, scale, measure, granularity.
  NOT for: method selection (方法選択 → Mekhanē S2).

triggers:
  - 粒度・スケールの決定
  - 測定基準の設定
  - 「どのレベルで見るか」
  - /met コマンド

keywords: [metron, measure, scale, metric, 測定, 粒度, スケール]

related:
  upstream:
    - "O1 Noēsis (X-OS1: 本質理解→スケール)"
    - "O2 Boulēsis (X-OS3: 目的定義→目標の大きさ)"
  downstream:
    - "P1 Khōra (X-SP1: 測定→適用領域を限定)"
    - "P2 Hodos (X-SP2: 測定→到達経路を制約)"
    - "K1 Eukairia (X-SK1: 測定→今が好機か)"
    - "K2 Chronos (X-SK2: 測定→時間スケール)"
    - "H1 Propatheia (X-SH1: スケール→大きすぎ/小さすぎの直感)"
    - "H2 Pistis (X-SH2: スケール→確信度)"

version: "3.0.0"
workflow_ref: ".agent/workflows/met.md"
risk_tier: L1
reversible: true
requires_approval: false
risks: ["none identified"]
fallbacks: ["manual execution"]
---

# S1: Metron (Μέτρον)

> **生成**: Internality × Scale
> **役割**: 測定基準・粒度を決定する
> **認知的意味**: 「どのスケールで見るか」— ズームレベルの起点

## ズームチェーンにおける位置

Metron はズーム伝播チェーンの**起点の一つ**:

```
O1/O2 (認識) → [X-OS1/3] → S1 Metron → [X-SP1/2]  → P (適用のズーム)
                                        → [X-SK1/2]  → K (タイミングのズーム)
                                        → [X-SH1/2]  → H (傾向のフィルター)
```

## Processing Logic

```
入力: 対象 / 目的
  ↓
[STEP 1] スケール候補の提示
  ├─ ミクロ: 要素レベル (関数, 行, 1つの概念)
  ├─ メゾ: コンポーネントレベル (モジュール, 機能)
  └─ マクロ: システムレベル (プロジェクト全体, アーキテクチャ)
  ↓
[STEP 2] 測定基準の定義
  ├─ 何を測るか (定量? 定性?)
  ├─ どう測るか (基準, 単位)
  └─ どの精度で (許容誤差)
  ↓
[STEP 3] ズーム伝播の確認
  └─ このスケールが P, K, H にどう影響するか
  ↓
出力: [スケール, 測定基準, 伝播影響]
```

## X-series 接続

> S1 は出力射が多い (6本)。ズームチェーンの起点として広く伝播する。

### 入力射

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-OS1 | O1 Noēsis | 本質理解→何をどのスケールで測るか | `/noe >> /met` |
| X-OS3 | O2 Boulēsis | 目的定義→目標の大きさを決める | `/bou >> /met` |

### 出力射 (6本)

| X | Target | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-SP1 | P1 Khōra | スケール→適用領域 (構造層) | `/met >> /kho` |
| X-SP2 | P2 Hodos | スケール→経路 (構造層) | `/met >> /hod` |
| X-SK1 | K1 Eukairia | スケール→好機 (構造層) | `/met >> /euk` |
| X-SK2 | K2 Chronos | スケール→時間 (構造層) | `/met >> /chr` |
| X-SH1 | H1 Propatheia | スケール→直感 (反省層) | `/met >> /pro` |
| X-SH2 | H2 Pistis | スケール→確信 (反省層) | `/met >> /pis` |

## CCL 使用例

```ccl
# 認識→スケール決定
/noe+{target: "96体系"} >> /met{level: "macro"}

# スケール→全方向伝播
/met{scale: "module"} >> /kho{scope: "current_project"}
/met{scale: "module"} >> /chr{timeframe: "sprint"}

# 振動: スケールと場を行き来
/met ~ /kho
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| スケールを固定したまま全てを見る | ズームの切り替えが必要。1つのスケールでは盲点が生じる |
| ズーム伝播を無視 | Metron の出力は6方向に影響する。全て確認すべき |
| 精度だけ追求 | 精度よりスケールの適切さが先 |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| micro | `/met.micro` | ミクロスケール固定 |
| macro | `/met.macro` | マクロスケール固定 |
| zoom | `/met.zoom` | スケール切替 |

---

*Metron: 古代ギリシャにおける「尺度・測定・節度」*
*v3.0: ズームチェーン起点 + 6出力射 (2026-02-07)*
