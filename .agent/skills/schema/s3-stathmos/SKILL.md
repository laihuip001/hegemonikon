---
# Theorem Metadata (v3.0)
id: "S3"
name: "Stathmos"
greek: "Σταθμός"
series: "Schema"
generation:
  formula: "Internality × Precision"
  result: "内在精密 — 評価基準の設定"

description: >
  何を基準に評価する？・成功条件を定義したい・ベンチマークを設定したい時に発動。
  Evaluation criteria setting, benchmark definition, success criteria.
  Use for: 基準, 評価, benchmark, criteria, standard.
  NOT for: scale/granularity (スケール → Metron S1).

triggers:
  - 評価基準の設定
  - 成功/失敗の判定条件定義
  - ベンチマーク設計
  - /sta コマンド

keywords: [stathmos, standard, benchmark, criterion, 基準, 評価, ベンチマーク]

related:
  upstream:
    - "O3 Zētēsis (X-OS5: 問いの発見→評価基準設定)"
    - "O4 Energeia (X-OS7: 行為の実行→成果基準定義)"
  downstream:
    - "P1 Khōra (X-SP3: 評価基準→評価対象の場)"
    - "P2 Hodos (X-SP4: 評価基準→達成への道筋)"
    - "K1 Eukairia (X-SK3: 評価基準→今が評価の好機か)"
    - "K2 Chronos (X-SK4: 評価基準→評価に必要な時間枠)"
    - "H3 Orexis (X-SH5: 基準→基準を満たしたい欲求)"
    - "H4 Doxa (X-SH6: 基準→基準の妥当性への信念)"

version: "3.0.0"
workflow_ref: ".agent/workflows/sta.md"
risk_tier: L1
reversible: true
requires_approval: false
risks: ["none identified"]
fallbacks: ["manual execution"]
---

# S3: Stathmos (Σταθμός)

> **生成**: Internality × Precision
> **役割**: 評価基準を設定する
> **認知的意味**: 「何をもって良しとするか」を先に決める

## Metron (S1) との区別

| | Metron (S1) | Stathmos (S3) |
|:--|:-----------|:-------------|
| 問い | 「どのスケールで見るか」 | 「何を基準に判定するか」 |
| 出力 | 粒度/スケール | 合格/不合格の閾値 |
| 例 | 「モジュール単位で見る」 | 「8項目カバー率で判定する」 |

## Processing Logic

```
入力: 評価対象 / 目標
  ↓
[STEP 1] 基準候補の列挙
  ├─ 定量基準: 数値で計測可能
  ├─ 定性基準: チェックリスト
  └─ 相対基準: 比較対象との差
  ↓
[STEP 2] 閾値の設定
  ├─ 最低基準: これを下回ると不合格
  ├─ 目標基準: 達成すべきレベル
  └─ 理想基準: 最高水準
  ↓
[STEP 3] ズーム伝播の確認
  └─ 基準のスケールが P, K, H に影響する (6方向)
  ↓
出力: [基準定義, 閾値, 判定方法]
```

## X-series 接続

> S3 は S1/S2 と同じく6本の出力射を持つズームチェーン起点。

### 入力射

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-OS5 | O3 Zētēsis | 問い→評価基準を設定 | `/zet >> /sta` |
| X-OS7 | O4 Energeia | 行為→成果基準を定義 | `/ene >> /sta` |

### 出力射 (6本)

| X | Target | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-SP3 | P1 Khōra | 評価のスケール→対象の場 (構造層) | `/sta >> /kho` |
| X-SP4 | P2 Hodos | 評価のスケール→達成経路 (構造層) | `/sta >> /hod` |
| X-SK3 | K1 Eukairia | 評価のスケール→好機 (構造層) | `/sta >> /euk` |
| X-SK4 | K2 Chronos | 評価のスケール→時間枠 (構造層) | `/sta >> /chr` |
| X-SH5 | H3 Orexis | 基準→基準を満たしたい欲求 (反省層) | `/sta >> /ore` |
| X-SH6 | H4 Doxa | 基準→基準の妥当性への信念 (反省層) | `/sta >> /dox` |

## CCL 使用例

```ccl
# 問いから評価基準を設定
/zet{question: "D1 完了の定義は？"} >> /sta{define: "8項目カバー率"}

# 基準→時間見積もり
/sta{criteria: "18 Skills 充実"} >> /chr{estimate: true}

# 基準と欲求の振動
/sta{criteria: "strict"} ~ /ore{want: "完璧にしたい"}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 基準なしに行動する | 「何をもって完了とするか」が先 |
| 基準を途中で変える | 基準変更は明示的に行う。暗黙の変更は自己欺瞞 |
| 理想基準だけ設定 | 最低基準も必要。理想は方向性、最低は判定 |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| quantitative | `/sta.quant` | 定量基準設定 |
| qualitative | `/sta.qual` | 定性基準設定 |
| comparative | `/sta.comp` | 相対基準 (比較) |


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

*Stathmos: 古代ギリシャにおける「秤・基準・宿場」*
*v3.0: ズームチェーン起点 + Metron区別 + 6出力射 (2026-02-07)*
