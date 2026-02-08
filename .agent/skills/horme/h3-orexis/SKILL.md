---
# Theorem Metadata (v3.0)
id: "H3"
name: "Orexis"
greek: "Ὄρεξις"
series: "Hormē"
generation:
  formula: "Value × Valence"
  result: "価値傾向 — 何を望み、何を避けるか"

description: >
  何を望んでいる？・欲求を明確にしたい・本当に欲しいものは何？時に発動。
  Desire identification, want clarification, appetitive drive analysis.
  Use for: 欲求, 望み, want, desire, 欲しい.
  NOT for: purpose (目的 → Telos K3), confidence (確信 → Pistis H2).

triggers:
  - 欲求の同定
  - 価値選好の明確化
  - 「何が欲しいのか」の問い
  - /ore コマンド

keywords: [orexis, desire, appetite, want, drive, 欲求, 望み]

related:
  upstream:
    - "O3 Zētēsis (X-OH5: 問いの探求→これが欲しいの発生)"
    - "O4 Energeia (X-OH7: 行為の完了→次に何を望むか)"
    - "S3 Stathmos (X-SH5: 基準設定→基準を満たしたい欲求)"
    - "S4 Praxis (X-SH7: 実践選択→実践したい/したくない)"
  downstream:
    - "A1 Pathos (X-HA3: 欲求→欲求の正体を感じ取る)"
    - "A2 Krisis (X-HA4: 欲求→欲求の妥当性を判定)"
    - "K1 Eukairia (X-HK3: 欲求→欲しいものに好機を見出す ⚠️)"
    - "K3 Telos (X-HK4: 欲求→欲求が目的を書き換える ⚠️)"

version: "3.0.0"
workflow_ref: ".agent/workflows/ore.md"
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "欲求による好機歪曲 (X-HK3)"
  - "欲求による目的上書き (X-HK4)"
fallbacks: ["manual execution"]
---

# H3: Orexis (Ὄρεξις)

> **生成**: Value × Valence
> **役割**: 何を望み、何を避けるかを同定する
> **認知的意味**: 「本当に欲しいものは何か」を正直に見つめる

## When to Use

### ✓ Trigger

- 「何がしたい」「何が欲しい」の明確化
- 優先順位の根拠を欲求から探るとき
- Creator の `/u` (意見を求める) の中核

### ✗ Not Trigger

- 目的の定義 → `/tel` (Telos)
- 確信度の評価 → `/pis` (Pistis)

## Processing Logic

```
入力: 状況 / 選択肢
  ↓
[STEP 1] 欲求の同定
  ├─ 接近的欲求: 何を得たいか
  └─ 回避的欲求: 何を避けたいか
  ↓
[STEP 2] 欲求の構造分析
  ├─ 表層欲求: 直接的な望み
  ├─ 深層欲求: その望みの裏にある本当の望み
  └─ 矛盾検出: 相反する欲求はあるか
  ↓
[STEP 3] 欲求→行動の変換可能性
  ├─ 充足可能: 行動で実現できる
  ├─ 制約付き: 条件を満たせば実現できる
  └─ 不可能: 構造的に実現不可
  ↓
出力: [欲求リスト, 深層構造, 行動推奨]
```

## X-series 接続

> **自然度**: 反省（注意を向ければ気づく遷移）

### 入力射

| X | Source | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-OH5 | O3 Zētēsis | 探求→「これが欲しい」の発生 | `/zet >> /ore` |
| X-OH7 | O4 Energeia | 行為完了→次に何を望むか | `/ene >> /ore` |
| X-SH5 | S3 Stathmos | 基準→基準を満たしたい欲求 | `/sta >> /ore` |
| X-SH7 | S4 Praxis | 実践→実践したい/したくない | `/pra >> /ore` |

### 出力射

| X | Target | 意味 | CCL |
|:--|:-------|:-----|:----|
| X-HA3 | A1 Pathos | 欲求→欲求の正体を感じ取る | `/ore >> /pat` |
| X-HA4 | A2 Krisis | 欲求→欲求の妥当性を判定 | `/ore >> /dia` |
| X-HK3 | K1 Eukairia ⚠️ | 欲求→欲しいものに好機を見出す | `/ore >> /euk` |
| X-HK4 | K3 Telos ⚠️ | 欲求→欲求が目的を書き換える | `/ore >> /tel` |

> ⚠️ **X-HK3, X-HK4 は認知バイアスの温床**。欲求が好機認識を歪め、目的を上書きする。必ず `/dia.epo` を挟む。

## CCL 使用例

```ccl
# 欲求の妥当性を検証
/ore{want: "96体系を美しくしたい"} >> /dia{check: "妥当か"}

# 欲求が目的を歪めていないか
/ore >> /tel _ /dia.epo{bias_check: "purpose hijacking?"}

# 行為完了後の次の欲求を探る
/ene{completed: true} >> /ore{what_next: true}
```

## アンチパターン

| ❌ | 理由 |
|:---|:-----|
| 欲求 = 目的と混同する | Orexis ≠ Telos。欲求は主観的、目的は客観的 |
| 欲求→好機宣言 (X-HK3) | 「欲しいから今がチャンス」は典型的バイアス |
| 欲求を否定する | 欲求は信号。否定ではなく観察して検証する |

## 派生モード

| Mode | CCL | 用途 |
|:-----|:----|:-----:|
| surface | `/ore.surface` | 表層欲求の同定 |
| deep | `/ore.deep` | 深層欲求の掘削 |
| conflict | `/ore.conflict` | 相反する欲求の検出 |

---

*Orexis: アリストテレスにおける「欲求」— 理性的欲求 (boulēsis) と感覚的欲求を含む*
*v3.0: X-series全接続 + バイアス警告 (2026-02-07)*
