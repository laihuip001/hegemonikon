---
# Theorem Metadata (v3.0)
id: "P3"
name: "Trokhia"
greek: "Τροχιά"
series: "Perigraphē"
generation:
  formula: "Function × Scale"
  result: "機能スケール — 反復サイクルの軌道"

description: >
  どの周期で繰り返す？・イテレーションサイクルを設計したい時に発動。
  Iteration cycle design, orbit planning, repetitive pattern definition.
  Use for: サイクル, 反復, iteration, orbit, 周期.
  NOT for: one-shot tasks (直線的な実行).

triggers:
  - 反復パターンの定義
  - イテレーションサイクルの設計
  - 軌道・周期の計画
  - /tro コマンド

keywords:
  - trokhia
  - orbit
  - cycle
  - iteration
  - trajectory
  - 軌道
  - 周期
  - サイクル

related:
  upstream:
    - "S2 Mekhanē (X-SP5: 方法→反復サイクル設計)"
    - "S4 Praxis (X-SP7: 実践→反復パターン)"
  downstream:
    - "K3 Telos (X-PK5: サイクル→反復の目的)"
    - "K4 Sophia (X-PK6: サイクル→反復に必要な知恵)"

implementation:
  micro: ".agent/workflows/tro.md"
  macro: "(future)"

version: "3.0.0"
workflow_ref: ".agent/workflows/tro.md"
risk_tier: L1
reversible: true
requires_approval: false
risks: ["none identified"]
fallbacks: ["manual execution"]
---

# P3: Trokhia (Τροχιά)

> **生成**: Function × Scale
> **役割**: 反復サイクルの軌道を定義する
> **認知的意味**: 「どの周期で、何を繰り返すか」を設計する

## When to Use

### ✓ Trigger

- イテレーションサイクルの設計 (スプリント, 日次, 週次)
- 改善ループの定義
- 反復する作業パターンの最適化
- 「何度もやっている」ことの構造化

### ✗ Not Trigger

- 一回限りのタスク → `/ene` で実行
- 道筋の定義 → `/hod` (Hodos: 一方向の経路)

## Processing Logic

```
入力: 反復的な活動/目標
  ↓
[STEP 1] サイクルの同定
  ├─ 周期: 分/時/日/週/月/四半期
  ├─ 内容: 各周期で何をするか
  └─ 変動: 各周期で何が変わるか
  ↓
[STEP 2] 軌道パラメータ
  ├─ 軌道長: 何回繰り返すか
  ├─ 収束条件: いつ軌道を離脱するか
  └─ フィードバック: 各周期の学習をどう反映するか
  ↓
[STEP 3] ズームレベル確認 (構造層)
  ├─ 方法のズーム (S) から伝播されたか → X-SP5
  └─ タイミングのズーム (K) と整合するか → X-PK5
  ↓
出力: [サイクル定義, 周期, 収束条件]
```

## X-series 接続

> **自然度**: 構造（意図的に操作するズームレベル伝播）

### ズームチェーン上の位置

```
S (方法のズーム) → [X-SP5/7] → P3 (軌道のズーム) → [X-PK5/6] → K (タイミングのズーム)
```

### 入力射

| X | Source | ズーム伝播 | CCL |
|:--|:-------|:-----------|:----|
| X-SP5 | S2 Mekhanē | 方法の粒度→サイクルの粒度 | `/mek >> /tro` |
| X-SP7 | S4 Praxis | 実践の粒度→反復パターンの粒度 | `/pra >> /tro` |

### 出力射

| X | Target | ズーム伝播 | CCL |
|:--|:-------|:-----------|:----|
| X-PK5 | K3 Telos | サイクルのスケール→目的のスケール | `/tro >> /tel` |
| X-PK6 | K4 Sophia | サイクルのスケール→知恵のスケール | `/tro >> /sop` |

## CCL 使用例

```ccl
# 方法から反復サイクルを導出
/mek+{method: "スプリント開発"} >> /tro{cycle: "2-week sprint"}

# サイクルの目的整合性を確認
/tro{cycle: "daily standup"} >> /tel{check: "目的と合っているか"}

# 振動: サイクルと方法を行き来して最適化
/mek ~ /tro
```

## アンチパターン

| ❌ やってはいけない | 理由 |
|:-------------------|:-----|
| サイクルなしに反復する | 無軌道の反復 = 惰性。Trokhia で構造化すべき |
| ズームミスマッチ | マクロ方法 + ミクロサイクル = 不整合。X-SP のズーム伝播を確認 |
| 収束条件なしの永久ループ | 軌道には離脱点が必要。「いつやめるか」を先に決める |
| Hodos (P2) との混同 | Trokhia = 周回、Hodos = 直線。目的が違う |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| sprint | `/tro.sprint` | スプリントサイクル設計 |
| daily | `/tro.daily` | 日次ルーチン設計 |
| feedback | `/tro.feedback` | フィードバックループ設計 |


## 🧠 WM (Working Memory) — 必須出力

> **SE原則**: 全 WF 出力に WM セクションを含めること（省略不可）

```markdown
## 🧠 WM (Working Memory)

$goal = {この WF 実行の目的}
$constraints = {制約・前提条件}
$decision = {主要な判断とその根拠}
$next = {次のアクション}
```
---

*Trokhia: 古代ギリシャにおける「軌道・車輪の跡・周回軌道」*
*v3.0: ズームチェーン統合 + X-series全接続 + アンチパターン (2026-02-07)*
