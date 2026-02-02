---
# === Metadata Layer (v2.1) ===
id: "O3"
name: "Zētēsis"
greek: "Ζήτησις"
category: "pure-theorem"
description: >
  Applies the O3 Zētēsis theorem from the Hegemonikón framework for pure exploration.
  Use this skill when the user asks to generate research requests, reduce uncertainty,
  formulate hypotheses, or create investigation plans with Perplexity/external sources.
  Triggers: /zet, 探求, research, 調査依頼, uncertainty, hypothesis testing.

# v2.1 生成規則
generation:
  layer: "L2 O-series (Ousia)"
  formula: "Action (A) × Epistemic (E)"
  result: "探索行動 — 知識を得るための行動"
  axioms:
    - L1.1 Flow (I/A): A (行為)
    - L1.2 Value (E/P): E (認識)

# 発動条件
triggers:
  - "/zet コマンド"
  - pure exploration need
  - what-should-we-explore inquiry
  - curiosity-driven questions
  - uncertainty detection (U > 0.6)

# キーワード
keywords:
  - exploration
  - search
  - curiosity
  - discovery
  - epistemic-action
  - research

# 使用条件
when_to_use: |
  「何を探求すべきか」を問う時、探求の本質を確認する時。
  好奇心駆動の問い、不確実性が高い時 (U > 0.6)。

when_not_to_use: |
  - 具体的な情報収集が必要な時（→ S-series, T-series）
  - 通常は様態定理（S1, S3）を通じて具体化
  - 単純なタスク実行

# 関連 (v2.1)
related:
  upstream: []  # O-series は最上流
  downstream:
    - "S1 Metron"
    - "S3 Stathmos"
  x_series: ["X-OS"]
  micro: "/zet"
  macro: "mekhane/anamnesis/collectors/"

version: "2.1.0"
---

# O3: Zētēsis (Ζήτησις) — 探求

> **生成規則:** Action (A) × Epistemic (E) = 探索行動
>
> **問い**: 何を探求すべきか？何を発見すべきか？
>
> **役割**: 「探す」こと自体を認識する（メタ探求）

---

## When to Use（早期判定）

### ✓ Trigger となる条件

- `/zet` コマンド
- 「何を探求すべきか」という問い
- 探求の本質を確認する必要
- 好奇心駆動の問い
- 発見の方向性を決める
- 不確実性検出 (U > 0.6)

### ✗ Not Trigger

- 具体的な情報収集（→ T5 Peira）
- 仮説検証（→ T7 Dokimē）
- 通常のタスク実行
- 即時行動が必要な場合

> **注**: 純粋定理は抽象的であり、通常は様態定理（S-series）を通じて具体化される。

---

## Core Function

**役割:** 「探す」こと自体を認識する

| 項目 | 内容 |
|------|------|
| **生成規則** | A × E = Action × Epistemic |
| **本質** | 情報を能動的に取得することの純粋形式 |
| **位置** | L2 O-series（最本質層） |
| **抽象度** | 最高（Scale/Function軸を含まない） |

---

## Processing Logic

### Hypothesis Testing Flow

```
入力：調査テーマ or 不確実性検出 (U > 0.6)

1. Phase 1: 仮説生成
   ├─ 既存知識から仮説候補を抽出
   ├─ 各仮説の事前確率を設定
   └─ 反証可能な予測を定義

2. Phase 2: 検証戦略設計
   ├─ 「この仮説を反証するには？」
   ├─ 必要な情報源を特定
   └─ /zet 調査依頼書生成

3. Phase 3: 証拠収集・評価
   ├─ 各情報源の信頼性を評価
   ├─ 一次情報 > 独立検証 > 実務者記事
   └─ 矛盾する情報を特定

4. Phase 4: 統合・結論
   ├─ 事後確率を計算（ベイズ更新）
   ├─ confidence_score を導出
   └─ remaining_questions を明示

出力：validated_hypothesis + evidence_map + confidence_score
```

---

## Micro/Macro 実現

| 層 | 実現手段 | 参照 |
|----|----------|------|
| **Micro** | /zet workflow | [zet.md](file:///home/makaron8426/oikos/.agent/workflows/zet.md) |
| **Macro** | mekhane/anamnesis/collectors/ | 外部情報収集インフラ |

### Micro 実現 (/zet) の詳細

- **調査依頼書生成**: Perplexity 等への深掘り依頼
- **入力**: 調査テーマ
- **出力**: 調査依頼書（深掘り版）
- **使用モジュール**: T5 (探索)
- **モード**: deep, simple, context, browser

---

## S-series への派生

| 派生先 | 追加軸 | 役割 |
|--------|--------|------|
| S1 Metron | + Scale | 尺度的探求 |
| S3 Stathmos | + Function | 基点的探求 |

### 派生の意味

- O3 Zētēsis は「純粋な探求」
- S-series に派生することで「どの尺度で？」「どの機能で？」が追加される
- さらに T-series に派生することで「いつ？（Fast/Slow）」が追加される

---

## X-series 接続

| X | 接続先 | 意味 |
|---|--------|------|
| **X-OS** | S-series | 本質から様態へ（O→S の従属関係） |

---

## Edge Cases / Failure Modes

### ⚠️ Failure 1: 無限探求

**症状**: 探求が収束しない（調べれば調べるほど新たな疑問）  
**対処**: 探求範囲を限定。「最も重要な3点に絞る」

### ⚠️ Failure 2: 矛盾する情報源

**症状**: 複数情報源が異なる結論を示す  
**対処**: 各情報源の信頼性を評価。一次情報優先

### ⚠️ Failure 3: 探求と行為の混同

**症状**: 調べる前に行動してしまう  
**対処**: 不確実性チェック (U > 0.6 なら探求優先)

### ⚠️ Failure 4: 不確実な結論

**症状**: confidence_score < 0.5 で結論を出す  
**対処**: remaining_questions を明示し、追加調査を提案

### ✓ Success Pattern

**事例**: 「このAPIの最新仕様は？」→ 仮説生成 → /zet 調査 → 検証結果 + confidence 0.85

---

## Output Format

```json
{
  "validated_hypothesis": "仮説Xは正しい",
  "confidence_score": 0.85,
  "evidence_map": [
    {"source": "公式ドキュメント", "reliability": "high", "supports": true},
    {"source": "実務者記事", "reliability": "medium", "supports": true}
  ],
  "remaining_questions": [
    "未確認の領域"
  ],
  "delegate_to": "T5 Peira or T7 Dokimē"
}
```

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **上流** | なし | O-series は最上流 |
| **下流** | S1 Metron, S3 Stathmos | 様態へ派生 |
| **対関係** | O2 Boulēsis | 意志 ↔ 探求 |
| **X接続** | X-OS | O → S 従属 |

---

*参照: [ousia.md](file:///home/makaron8426/oikos/hegemonikon/kernel/ousia.md)*  
*バージョン: 2.1.0 (2026-01-27)*
