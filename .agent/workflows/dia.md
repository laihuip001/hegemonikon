---
description: A2 Krisis（判定力）を発動する抽象コマンド。敵対的レビュー機能統合。
hegemonikon: A2 Krisis
version: "7.0"
lcm_state: stable       # draft | beta | stable | deprecated
layer: "Δ"
derivatives: [aff, neg, epo, root, devil, steelman, counterfactual, cold_mirror, deliberative]
cognitive_algebra:
  "+": 詳細判定（証拠/論拠/反論を完全展開）
  "-": 判定要約（PASS/FAIL + 1行理由）
  "*": メタ判定（判定プロセス自体を判定）
---

# /dia: A2 Krisis 発動コマンド

> **Hegemonikón**: A2 Krisis（判定力）
> **層**: Δ（デルタ）— 抽象コマンド
> **役割**: 判定・検証・批評の能力を発動する
>
> **制約**: モード未指定時は自動選択ロジックを使用する。判定後は必ず確信度を明示すること。

---

## サブモジュール

| ファイル | 内容 |
|----------|------|
| [basic-modes.md](dia/basic-modes.md) | 基本モード (aff/neg/root/devil/steelman/counterfactual) |
| [advanced-modes.md](dia/advanced-modes.md) | 高度モード (epochē/audit/panorama/cross-model/cold_mirror/deliberative) |

---

## Cognitive Algebra

| Operator | Meaning | Output |
|:---------|:--------|:-------|
| `/dia+` | **Deepening** | 詳細判定: 証拠、論拠、反論を完全展開 |
| `/dia-` | **Reduction** | 要約判定: PASS/FAIL + 1行理由 |
| `/dia*` | **Expansion** | メタ判定: 「この判定は正当か」を判定 |

---

## モード一覧

### 基本モード

| モード | 説明 | 発動 |
|:-------|:-----|:-----|
| `aff` | 肯定的判定 | 「良い点は」 |
| `neg` | 否定的判定 | 「問題点は」 |
| `root` | 根源探索 | 「そもそも」 |
| `devil` | 悪魔の代弁者 | 「反論して」 |
| `steelman` | 最強論証 | 「最強の形で」 |
| `counterfactual` | 反実仮想 | 「もし」 |

### 高度モード

| モード | 説明 | 発動 |
|:-------|:-----|:-----|
| `epochē` | 判断停止 | 「確信度を宣言」 |
| `audit` | 消化品質診断 | 「消化できてる？」 |
| `panorama` | 6層メタ認知スキャン | 「盲点」「見落とし」 |
| `cross-model` | Cross-Model Verification | 「別のAI」 |
| `cold_mirror` | 冷徹な鏡 | 「厳しく」 |
| `deliberative` | 三視点反復改善 | 「反復改善」 |

---

## 発動条件

| トリガー | 動作 |
|:---------|:-----|
| `/dia` | 状況に応じてモード自動選択 |
| `/dia --mode={mode}` | 特定モード実行 |
| `/dia {mode}` | 特定モード実行（省略形） |

---

## 自動選択ロジック

> モード未指定時、文脈から最適モードを提案する。

```yaml
if 統合・マージ・吸収 の話題:
  → --mode=audit (消化品質診断)

if Gemini/Jules の成果物:
  → --mode=cross-model (Cross-Model 監査)

if 空虚語・抽象論 を検出:
  → Buzzword Guillotine 発動

if 確信度が LOW or 認識限界を検出:
  → --mode=epochē (判断停止)

if 盲点・見落とし を問う:
  → --mode=panorama (6層スキャン)

if 認知歪み・論理的欠陥・甘え を指摘すべき:
  → --mode=cold_mirror (冷徹な鏡)

default:
  → ユーザーに確認（提案付き）
```

---

## 自動提案の出力形式

| 項目 | 内容 |
|:-----|:-----|
| 文脈分析 | 検出したキーワード/パターン |
| 推奨モード | `--mode={mode}` |
| 理由 | なぜこのモードか |
| 確認 | このまま実行 / 代替モード / キャンセル |

---

## Hegemonikón Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| A2 Krisis | /dia | v7.1 Ready |

> **制約リマインダ**: 判定後は確信度を明示すること [Certain/Estimated/Hypothetical]。

---

*v7.1 — FBR 適用 (2026-02-07)*
