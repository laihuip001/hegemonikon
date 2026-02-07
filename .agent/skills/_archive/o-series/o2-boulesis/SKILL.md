---
# === Metadata Layer (v2.1) ===
id: "O2"
name: "Boulēsis"
greek: "Βούλησις"
category: "pure-theorem"
description: >
  Applies the O2 Boulēsis theorem from the Hegemonikón framework for pure will clarification.
  Use this skill when the user asks to clarify goals, define what they truly want,
  align values with actions, or identify the deepest purpose behind a task.
  Triggers: /bou, 意志, goal clarification, 何を望むか, purpose, value alignment.

# v2.1 生成規則
generation:
  layer: "L2 O-series (Ousia)"
  formula: "Inference (I) × Pragmatic (P)"
  result: "意志推論 — 目標設定のための思考"
  axioms:
    - L1.1 Flow (I/A): I (推論)
    - L1.2 Value (E/P): P (実用)

# 発動条件
triggers:
  - "/bou コマンド"
  - goal clarification
  - what-do-we-want inquiry
  - value alignment check
  - "何を望むか" inquiry

# キーワード
keywords:
  - will
  - intention
  - desire
  - goal
  - pragmatic
  - purpose

# 使用条件
when_to_use: |
  「何を達成したいか」を問う時、目標の本質を確認する時。
  意志の純粋形式を問う場合、作業一段落時、方向性の迷いがある時。

when_not_to_use: |
  - 具体的な判断が必要な時（→ S-series, T-series）
  - 通常は様態定理（S2, S4）を通じて具体化
  - 単純なタスク実行

# 関連 (v2.1)
related:
  upstream: []  # O-series は最上流
  downstream:
    - "S2 Mekhanē"
    - "S4 Praxis"
  x_series: ["X-OS"]
  micro: "/bou"
  macro: "mekhane/boulesis/"

version: "2.1.0"
risk_tier: L0
reversible: true
requires_approval: false
risks:
  - "アーカイブ済みスキルの誤参照による古い手法の適用"
fallbacks: []
---

# O2: Boulēsis (Βούλησις) — 意志

> **生成規則:** Inference (I) × Pragmatic (P) = 意志推論
>
> **問い**: 何を達成したいか？何を望むか？
>
> **役割**: 「望む」こと自体を認識する（メタ意志）

---

## When to Use（早期判定）

### ✓ Trigger となる条件

- `/bou` コマンド
- 「何を達成したいか」という問い
- 目標の本質を確認する必要
- 価値観・意図の確認
- 意志のメタ分析
- 作業一段落時、方向性の迷い

### ✗ Not Trigger

- 具体的な優先判断（→ T2 Krisis）
- 戦略設計（→ T4 Phronēsis）
- 通常のタスク実行
- 即時行動が必要な場合

> **注**: 純粋定理は抽象的であり、通常は様態定理（S-series）を通じて具体化される。

---

## Core Function

**役割:** 「望む」こと自体を認識する

| 項目 | 内容 |
|------|------|
| **生成規則** | I × P = Inference × Pragmatic |
| **本質** | 目標を持つことの純粋形式 |
| **位置** | L2 O-series（最本質層） |
| **抽象度** | 最高（Scale/Function軸を含まない） |

---

## Processing Logic

### Socratic Questioning Flow

```
入力：「〇〇したい」（曖昧な表現）

1. Phase 1: 前提掘出
   ├─ 「それって、本当に〇〇ですか？」
   ├─ 暗黙の仮定・価値観を抽出
   └─ 候補目標を3-5個列挙

2. Phase 2: 深掘り質問
   ├─ 「もし実現できたら、次は何をしたい？」
   ├─ 「それより優先すべき目標はありますか？」
   └─ 各目標の整合性・実現性を評価（0-100スコア）

3. Phase 3: Assumption Reversal
   └─ 「その正反対が成立したら、どうなる？」
   └─ 根本的価値を問い直す

4. Phase 4: 統合・確定
   ├─ 複数目標が競合 → 根本価値で統約
   └─ 最終目標宣言 + 初期ステップ

出力：明確化された目標 + alignment_score + 次のアクション
```

---

## Micro/Macro 実現

| 層 | 実現手段 | 参照 |
|----|----------|------|
| **Micro** | /bou workflow | [bou.md](file:///home/makaron8426/oikos/.agent/workflows/bou.md) |
| **Macro** | mekhane/boulesis/ | (将来実装) 目標履歴・価値関数更新 |

### Micro 実現 (/bou) の詳細

- **6フェーズ構造**: 意志明確化フロー
- **入力**: 領域（任意）
- **出力**: 優先順位付き目標リスト + 次のアクション
- **使用モジュール**: — (純粋思考)

---

## S-series への派生

| 派生先 | 追加軸 | 役割 |
|--------|--------|------|
| S2 Mekhanē | + Function | 方法論的意志 |
| S4 Praxis | + Scale | 実践的意志 |

### 派生の意味

- O2 Boulēsis は「純粋な意志」
- S-series に派生することで「どの機能で？」「どの尺度で？」が追加される
- さらに T-series に派生することで「いつ？（Fast/Slow）」が追加される

---

## X-series 接続

| X | 接続先 | 意味 |
|---|--------|------|
| **X-OS** | S-series | 本質から様態へ（O→S の従属関係） |

---

## Edge Cases / Failure Modes

### ⚠️ Failure 1: 目標不明

**症状**: 「何を望むか」が明確にならない  
**対処**: Socratic質問を繰り返す。最大3ラウンドで停止

### ⚠️ Failure 2: 目標矛盾

**症状**: 複数目標が矛盾（alignment_score < 0.5）  
**対処**: 「どちらの価値観が本来的か」を深掘り。究極的には1軸に統約

### ⚠️ Failure 3: 手段と目的の混同

**症状**: 手段を目的として認識  
**対処**: 「なぜ？」を繰り返し問う（/why 連携）

### ⚠️ Failure 4: 実現不可能な目標

**症状**: 制約条件を超える目標が設定される  
**対処**: 制約を明示 → 代替目標を提案 or 目標再定義

### ✓ Success Pattern

**事例**: 「何を達成したい？」→ Socratic 3ラウンド → 目標 + alignment_score 0.87 → S/T-series へ

---

## Output Format

```json
{
  "clarified_goal": "〇〇を達成する",
  "alignment_score": 0.87,
  "core_rationale": "この目標が選ばれた根本理由（1-2文）",
  "initial_steps": [
    "具体的第1ステップ",
    "具体的第2ステップ"
  ],
  "uncertainty": {
    "areas": ["潜在的な問題"],
    "mitigation_strategy": "それに対する対処"
  },
  "delegate_to": "S2 Mekhanē or T4 Phronēsis"
}
```

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **上流** | なし | O-series は最上流 |
| **下流** | S2 Mekhanē, S4 Praxis | 様態へ派生 |
| **対関係** | O1 Noēsis | 認識 ↔ 意志 |
| **X接続** | X-OS | O → S 従属 |

---

*参照: [ousia.md](file:///home/makaron8426/oikos/hegemonikon/kernel/ousia.md)*  
*バージョン: 2.1.0 (2026-01-27)*
