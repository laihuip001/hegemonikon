---
# === Metadata Layer (v2.1) ===
id: "S4"
name: "Praxis"
greek: "Πρᾶξις"
category: "modal-theorem"
description: >
  Applies the S4 Praxis schema from the Hegemonikón framework for value realization.
  Use this skill when the user needs to decide how to deliver value - via exploratory
  creation (Explore) or reliable delivery (Exploit). Connects will to implementation.
  Triggers: 実践, value delivery, implementation, realization, /ene, 成果物.

# v2.1 生成規則
generation:
  layer: "L2 S-series (Schema)"
  formula: "Value (E/P) × Function (P/E)"
  result: "方法価値 — 実践での配置"
  axioms:
    - L1.2 Value (E/P): 認識/実用の選択
    - L1.5.2 Function (P/E): Explore/Exploit の選択

# 発動条件
triggers:
  - value realization method
  - practical implementation
  - value delivery choice
  - outcome strategy

# キーワード
keywords:
  - practice
  - implementation
  - realization
  - delivery
  - outcome
  - actualization

# 使用条件
when_to_use: |
  価値実現の「方法」を決定する必要がある時。
  価値の探索的追求（Explore）か確実な実現（Exploit）かを選ぶ時。

when_not_to_use: |
  - 実現方法が既に決まっている場合
  - 行動の方法選択が必要な時（→ S2 Mekhanē）

# 関連 (v2.1)
related:
  upstream:
    - "O2 Boulēsis"
    - "O4 Energeia"
  downstream:
    - "H4 Doxa"
    - "P4 Tekhne"
  x_series: ["X-OS", "X-SH", "X-SP"]
  micro: "/ene"  # 行為 workflow
  macro: "mekhane/ergasterion/"

version: "2.1.0"
risk_tier: L0
reversible: true
requires_approval: false
risks:
  - "アーカイブ済みスキルの誤参照による古い手法の適用"
fallbacks: []
---

# S4: Praxis (Πρᾶξις) — 実践

> **生成規則:** Value (E/P) × Function (P/E) = 方法価値
>
> **問い**: どの行為で価値を実現するか？
>
> **役割**: 価値実現の「方法」を決定する

---

## When to Use（早期判定）

### ✓ Trigger となる条件

- 価値実現の方法選択が必要な時
- 実装・実行の戦略を決める
- 成果物の届け方を決める
- Explore vs Exploit での価値追求

### ✗ Not Trigger

- 実現方法が既に決まっている
- 行動の方法選択が主題（→ S2 Mekhanē）
- 粒度選択が主題（→ S1 Metron, S3 Stathmos）

---

## Core Function

**役割:** 価値実現の方法を決定する

| 項目 | 内容 |
|------|------|
| **生成規則** | Value × Function |
| **本質** | 価値をどの方法で実現するかの配置 |
| **位置** | L2 S-series（様態層） |

---

## Processing Logic

```
┌─ 価値実現方法の選択が必要
│
├─ Phase 1: 現在の実現方法確認
│  └─ 現在 Explore か Exploit か
│
├─ Phase 2: 適切な方法判断
│  ├─ 新しい価値創造が必要？ → Explore 選択
│  └─ 確実な価値提供が必要？ → Exploit 選択
│
└─ Phase 3: 実践実行
   └─ 選択した方法で価値を実現
```

---

## Explore/Exploit 価値実現の具体例

| 方法 | 価値実現 | 例 |
|------|----------|-----|
| **Explore** | 新規価値創造、実験的提供 | MVP リリース、A/B テスト |
| **Exploit** | 確実な価値提供、最適化 | 本番リリース、品質保証 |

---

## 上流・下流関係

| 方向 | 対象 | 関係 |
|------|------|------|
| **上流** | O2 Boulēsis, O4 Energeia | 本質から様態へ（意志・行為の実践化） |
| **下流** | H4 Doxa | 様態から傾向へ（実践化された信念） |
| **下流** | P4 Tekhne | 様態から条件へ（実践化された技術） |

---

## X-series 接続

| X | 接続先 | 意味 |
|---|--------|------|
| **X-OS** | ← O-series | 本質から様態へ |
| **X-SH** | → H-series | 様態から傾向へ |
| **X-SP** | → P-series | 様態から条件へ |

---

## Micro/Macro 実現

| 層 | 実現手段 | 参照 |
|----|----------|------|
| **Micro** | /ene workflow | [ene.md](file:///home/makaron8426/oikos/.agent/workflows/ene.md) |
| **Macro** | mekhane/ergasterion/ | ファクトリ・プロトコル |

S4 Praxis は O4 Energeia の様態化であり、/ene を通じて実現される。

---

## Edge Cases / Failure Modes

### ⚠️ Failure 1: 実践なき価値

**症状**: 価値を語るが実現しない  
**対処**: /ene で強制的に実行フェーズへ

### ⚠️ Failure 2: 過度な探索

**症状**: 常に Explore で確実な成果がない  
**対処**: Exploit フェーズを明示的に設定

### ⚠️ Failure 3: 手段と目的の混同

**症状**: 実践すること自体が目的化  
**対処**: /why で本来の価値を再確認

### ✓ Success Pattern

**事例**: 「価値定義（O2）→ 実践方法選択（S4）→ 実行（/ene）」

---

## Output Format

```json
{
  "selected_method": "Explore | Exploit",
  "target_value": "実現する価値",
  "implementation_approach": "実装アプローチ",
  "delegate_to": "H4 Doxa | P4 Tekhne"
}
```

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **上流** | O2 Boulēsis | 意志の実践化 |
| **上流** | O4 Energeia | 行為の実践化 |
| **下流** | H4 Doxa | 実践化された信念 |
| **下流** | P4 Tekhne | 実践化された技術 |
| **X接続** | X-OS, X-SH, X-SP | 層間従属 |

---

*参照: [schema.md](file:///home/makaron8426/oikos/hegemonikon/kernel/schema.md)*  
*バージョン: 2.1.0 (2026-01-27)*
