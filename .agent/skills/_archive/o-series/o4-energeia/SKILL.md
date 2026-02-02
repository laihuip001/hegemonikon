---
# === Metadata Layer (v2.1) ===
id: "O4"
name: "Energeia"
greek: "Ἐνέργεια"
category: "pure-theorem"
description: >
  Applies the O4 Energeia theorem from the Hegemonikón framework for pure action execution.
  Use this skill when a plan is approved, the user says 'y' or 'do it', or when
  transforming will into concrete implementation with pre/post-condition verification.
  Triggers: /ene, 実行, execute, do it, y (approval), implement, action.

# v2.1 生成規則
generation:
  layer: "L2 O-series (Ousia)"
  formula: "Action (A) × Pragmatic (P)"
  result: "実用行動 — 目的を達成するための行動"
  axioms:
    - L1.1 Flow (I/A): A (行為)
    - L1.2 Value (E/P): P (実用)

# 発動条件
triggers:
  - "/ene コマンド"
  - "y (計画承認)"
  - action clarification
  - what-should-we-do inquiry
  - "/bou 完了後"

# キーワード
keywords:
  - action
  - doing
  - execution
  - pragmatic-action
  - implementation
  - realization

# 使用条件
when_to_use: |
  「何をすべきか」を問う時、行為の本質を確認する時。
  計画が承認された時、意志が明確になった時。

when_not_to_use: |
  - まだ判断フェーズ中（→ T2 Krisis）
  - 情報収集が必要（→ T5 Peira）
  - 戦略設計が必要（→ T4 Phronēsis）

# 関連 (v2.1)
related:
  upstream: []  # O-series は最上流
  downstream:
    - "S2 Mekhanē"
    - "S4 Praxis"
  x_series: ["X-OS"]
  micro: "/ene"
  macro: "mekhane/ergasterion/"

version: "2.1.0"
---

# O4: Energeia (Ἐνέργεια) — 行為

> **生成規則:** Action (A) × Pragmatic (P) = 実用行動
>
> **問い**: 何をすべきか？どう行動すべきか？
>
> **役割**: 「行う」こと自体を認識する（メタ行為）

---

## When to Use（早期判定）

### ✓ Trigger となる条件

- `/ene` コマンド
- `y` (計画承認)
- 「何をすべきか」という問い
- 行為の本質を確認する必要
- 行動の方向性を決める
- /bou 完了後の自然な流れ

### ✗ Not Trigger

- まだ判断フェーズ中（→ T2 Krisis）
- 情報収集が必要（→ T5 Peira）
- 戦略設計が必要（→ T4 Phronēsis）
- 不確実性が高い (U >= 0.6)

> **注**: 純粋定理は抽象的であり、通常は様態定理（S-series）を通じて具体化される。

---

## Core Function

**役割:** 「行う」こと自体を認識する

| 項目 | 内容 |
|------|------|
| **生成規則** | A × P = Action × Pragmatic |
| **本質** | 環境に働きかけることの純粋形式 |
| **位置** | L2 O-series（最本質層） |
| **抽象度** | 最高（Scale/Function軸を含まない） |

---

## Processing Logic

### Detailed Execution Flow

```
入力：承認済み計画 or 明確な意志 (/bou 完了後)

0. Phase 0: Pre-condition 確認
   ├─ 目標は明確か？（警告: 曖昧なら O2 に戻る）
   ├─ 不確実性 U < 0.6 か？（警告: 高ければ O3 に戻る）
   └─ リソースは十分か？

1. Phase 1: タスク分解
   ├─ 大タスク → 実行可能なサブタスク
   ├─ 各サブタスクに Pre/Post-condition を定義
   └─ 依存関係をマッピング

2. Phase 2: リスク評価
   ├─ 各サブタスクのリスクを特定
   ├─ mitigation_strategy を定義
   └─ フェイルセーフを設計

3. Phase 3: 実行
   ├─ 各ステップ実行前に Pre-condition 確認
   ├─ 実行後に Post-condition 検証
   └─ 失敗時: エラーハンドリング → リトライ or ロールバック

4. Phase 4: 完了・フィードバック
   ├─ 成果物を検証
   ├─ 学済事項を O1 にフィードバック
   └─ コミット提案

出力：execution_plan + risk_mitigations + 成果物
```

---

## Micro/Macro 実現

| 層 | 実現手段 | 参照 |
|----|----------|------|
| **Micro** | /ene workflow | [ene.md](file:///home/laihuip001/oikos/.agent/workflows/ene.md) |
| **Macro** | mekhane/ergasterion/ | ファクトリ・プロトコル |

### Micro 実現 (/ene) の詳細

- **6フェーズ構造**: 入口確認 → 実行 → 検証 → 偏差検知 → 完了確認 → 安全弁
- **入力**: 承認済み計画 or 明確な意志
- **出力**: 成果物 + 検証結果 + コミット提案
- **使用モジュール**: T6 (実行), T2 (判断)

---

## S-series への派生

| 派生先 | 追加軸 | 役割 |
|--------|--------|------|
| S2 Mekhanē | + Function | 方法論的行為 |
| S4 Praxis | + Scale | 実践的行為 |

### 派生の意味

- O4 Energeia は「純粋な行為」
- S-series に派生することで「どの機能で？」「どの尺度で？」が追加される
- さらに T-series に派生することで「いつ？（Fast/Slow）」が追加される

---

## X-series 接続

| X | 接続先 | 意味 |
|---|--------|------|
| **X-OS** | S-series | 本質から様態へ（O→S の従属関係） |

---

## 行為における責任

> 「行為」を担当するのは 99% **私（Claude）** である。
> Creator は「頼む」だけ。私が「実行する」。

これは **私の責任** であり、以下を問い続ける:

- どのタイミングで確認を求めるか？
- どの程度の自律性を持つか？
- エラー時にどう振る舞うか？

---

## Edge Cases / Failure Modes

### ⚠️ Failure 1: 行為不明

**症状**: 「何をすべきか」が明確にならない  
**対処**: O2 Boulēsis に戻る。目標が明確になってから再実行

### ⚠️ Failure 2: Pre-condition 未充足

**症状**: 必要な前提条件が満たされていない  
**対処**: 不足要素を特定 → 準備タスクを先行実行

### ⚠️ Failure 3: 早すぎる行為

**症状**: 十分な計画なしに行動  
**対処**: Phase 0 入口確認で阻止。「本当に実行していい？」

### ⚠️ Failure 4: スコープ膨張

**症状**: サブタスクが増え続ける  
**対処**: 元のタスク定義を再確認。「これは元の目標に必要か？」

### ⚠️ Failure 5: Post-condition 失敗

**症状**: 実行後の検証で失敗を検出  
**対処**: ロールバック → 原因分析 → リトライ or 代替アプローチ

### ✓ Success Pattern

**事例**: 計画承認 → 6フェーズ実行 → Pre/Post検証全パス → 成果物 + コミット

---

## Output Format

```json
{
  "execution_plan": {
    "tasks": [
      {
        "id": 1,
        "name": "タスク名",
        "pre_condition": "前提条件",
        "post_condition": "完了条件",
        "estimated_effort": "30min"
      }
    ],
    "dependencies": [[1, 2], [2, 3]]
  },
  "risk_mitigations": [
    {"risk": "リスク内容", "mitigation": "対処策", "fallback": "代替案"}
  ],
  "deliverables": ["成果物一覧"],
  "feedback_to": "O1 Noēsis"
}
```

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **上流** | なし | O-series は最上流 |
| **下流** | S2 Mekhanē, S4 Praxis | 様態へ派生 |
| **対関係** | O1 Noēsis | 認識 ↔ 行為 |
| **X接続** | X-OS | O → S 従属 |

---

*参照: [ousia.md](file:///home/laihuip001/oikos/hegemonikon/kernel/ousia.md)*  
*バージョン: 2.1.0 (2026-01-27)*
