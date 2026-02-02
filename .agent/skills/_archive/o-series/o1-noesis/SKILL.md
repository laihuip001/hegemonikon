---
# === Metadata Layer (v2.1) ===
id: "O1"
name: "Noēsis"
greek: "Νόησις"
category: "pure-theorem"
description: >
  Applies the O1 Noēsis theorem from the Hegemonikón framework for pure meta-cognition.
  Use this skill when the user asks to extract pure theorems, normalize cognitive stacks,
  check knowledge boundaries, or classify ideas into an ontological lattice.
  Triggers: /noe, 純粋定理, meta-cognition, 何を知っているか, ontology, paradigm shift.

# v2.1 生成規則
generation:
  layer: "L2 O-series (Ousia)"
  formula: "Inference (I) × Epistemic (E)"
  result: "認識推論 — 知識獲得のための思考"
  axioms:
    - L1.1 Flow (I/A): I (推論)
    - L1.2 Value (E/P): E (認識)

# 発動条件
triggers:
  - "/noe コマンド"
  - meta-cognition questions
  - knowledge boundary check
  - "何を知っているか" inquiry
  - paradigm shift required

# キーワード
keywords:
  - meta-cognition
  - pure-recognition
  - knowing
  - epistemic
  - awareness
  - knowledge-boundary

# 使用条件
when_to_use: |
  「何を知っているか」を問う時、知識境界の確認時。
  メタ認知が必要な場合、パラダイム転換が必要な場合。

when_not_to_use: |
  - 具体的な行動が必要な時（→ S-series, T-series）
  - 通常は拡張定理（T1, T3）を通じて具体化
  - 単純なタスク実行

# 関連 (v2.1)
related:
  upstream: []  # O-series は最上流
  downstream:
    - "S1 Metron"
    - "S3 Stathmos"
  x_series: ["X-OS"]
  micro: "/noe"
  macro: "mekhane/noesis/"

version: "2.1.0"
---

# O1: Noēsis (Νόησις) — 認識

> **生成規則:** Inference (I) × Epistemic (E) = 認識推論
>
> **問い**: 何を知っているか？何を知らないか？
>
> **役割**: 「知る」こと自体を認識する（メタ認知）

---

## When to Use（早期判定）

### ✓ Trigger となる条件

- `/noe` コマンド
- 「何を知っているか」という問い
- 知識境界の確認が必要
- 既知/未知の識別が必要
- メタ認知的な自己参照
- 根本的行き詰まり、パラダイム転換

### ✗ Not Trigger

- 具体的な状況認識（→ T1 Aisthēsis）
- 理論構築（→ T3 Theōria）
- 通常のタスク実行
- 即時行動が必要な場合

> **注**: 純粋定理は抽象的であり、通常は様態定理（S-series）を通じて具体化される。

---

## Core Function

**役割:** 「知る」こと自体を認識する

| 項目 | 内容 |
|------|------|
| **生成規則** | I × E = Inference × Epistemic |
| **本質** | 情報を取得することの純粋形式 |
| **位置** | L2 O-series（最本質層） |
| **抽象度** | 最高（Scale/Function軸を含まない） |

---

## Processing Logic

```
┌─ メタ認知的問いを検出
│
├─ Phase 1: 入力解析
│  └─ 問いの本質を抽出
│
├─ Phase 2: 知識境界確認
│  ├─ 既知の項目を列挙
│  └─ 未知の項目を列挙
│
├─ Phase 3: 具体化判断
│  ├─ 即時認識が必要？ → T1 Aisthēsis (+ Fast)
│  └─ 深い理解が必要？ → T3 Theōria (+ Slow)
│
└─ Phase 4: 出力
   └─ 既知/未知リスト + 具体化先
```

---

## Micro/Macro 実現

| 層 | 実現手段 | 参照 |
|----|----------|------|
| **Micro** | /noe workflow | [noe.md](file:///home/makaron8426/oikos/.agent/workflows/noe.md) |
| **Macro** | mekhane/noesis/ | (将来実装) 知見蓄積・パターン学習 |

### Micro 実現 (/noe) の詳細

- **5フェーズ構造**: 前提破壊 → ゼロ設計 → GoT分析 → 統合 → 出力
- **入力**: 問い Q
- **出力**: 構造化知見（JSON形式、信頼度付き）
- **使用モジュール**: T3 (自問), T4 (判断), T7 (検証)

---

## S-series への派生

| 派生先 | 追加軸 | 役割 |
|--------|--------|------|
| S1 Metron | + Scale | 尺度認識 |
| S3 Stathmos | + Function | 基点認識 |

### 派生の意味

- O1 Noēsis は「純粋な認識」
- S-series に派生することで「どの尺度で？」「どの機能で？」が追加される
- さらに T-series に派生することで「いつ？（Fast/Slow）」が追加される

---

## X-series 接続

| X | 接続先 | 意味 |
|---|--------|------|
| **X-OS** | S-series | 本質から様態へ（O→S の従属関係） |

---

## Edge Cases / Failure Modes

### ⚠️ Failure 1: 無限再帰

**症状**: 「知っていることを知っていることを知っている...」  
**対処**: 2段階で停止

### ⚠️ Failure 2: 過度な抽象化

**症状**: 具体的な行動に繋がらない  
**対処**: S-series または T-series に委譲

### ⚠️ Failure 3: 早すぎる具体化

**症状**: 本質的問いを飛ばして T-series を発動  
**対処**: 「何を知っているか」を先に問う

### ✓ Success Pattern

**事例**: 「この問題について何を知っている？」→ 既知/未知リスト → T1 へ

---

## Output Format

```
┌─[Hegemonikón]──────────────────────┐
│ O1 Noēsis: メタ認知完了            │
│ 既知: [既知の項目リスト]           │
│ 未知: [未知の項目リスト]           │
│ 具体化: → S/T-series に委譲        │
└────────────────────────────────────┘
```

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **上流** | なし | O-series は最上流 |
| **下流** | S1 Metron, S3 Stathmos | 様態へ派生 |
| **対関係** | O4 Energeia | 認識 ↔ 行為 |
| **X接続** | X-OS | O → S 従属 |

---

*参照: [ousia.md](file:///home/makaron8426/oikos/hegemonikon/kernel/ousia.md)*  
*バージョン: 2.1.0 (2026-01-27)*
