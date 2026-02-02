---
# === Metadata Layer (v2.1) ===
id: "S2"
name: "Mekhanē"
greek: "Μηχανή"
category: "modal-theorem"
description: >
  Applies the S2 Mekhanē schema from the Hegemonikón framework for method selection.
  Use this skill when the user needs to choose between Explore (new approaches) or Exploit
  (proven methods), select strategy, or decide approach for problem-solving.
  Triggers: 方法, strategy, explore vs exploit, どうやって, /plan, approach.

# v2.1 生成規則
generation:
  layer: "L2 S-series (Schema)"
  formula: "Flow (I/A) × Function (P/E)"
  result: "方法流動 — 機構での配置"
  axioms:
    - L1.1 Flow (I/A): 推論/行為の選択
    - L1.5.2 Function (P/E): Explore/Exploit の選択

# 発動条件
triggers:
  - method selection required
  - explore vs exploit choice
  - strategy selection
  - approach decision

# キーワード
keywords:
  - method
  - mechanism
  - explore
  - exploit
  - strategy
  - approach

# 使用条件
when_to_use: |
  認知の「戦略」を決定する必要がある時。
  新しい手法の探索（Explore）か既知の手法の活用（Exploit）かを選ぶ時。

when_not_to_use: |
  - 方法が既に決まっている場合
  - スケール選択が必要な時（→ S1 Metron）

# 関連 (v2.1)
related:
  upstream:
    - "O2 Boulēsis"
    - "O4 Energeia"
  downstream:
    - "H2 Pistis"
    - "P2 Hodos"
  x_series: ["X-OS", "X-SH", "X-SP"]
  micro: "/plan"  # 戦略設計 workflow
  macro: null

version: "2.1.0"
---

# S2: Mekhanē (Μηχανή) — 機構

> **生成規則:** Flow (I/A) × Function (P/E) = 方法流動
>
> **問い**: どの方法で認知を配置するか？
>
> **役割**: 認知の「戦略」を決定する

---

## When to Use（早期判定）

### ✓ Trigger となる条件

- 方法選択が必要な時
- Explore vs Exploit の判断が必要
- 戦略・アプローチの決定
- 新規 vs 既存の手法選択

### ✗ Not Trigger

- 方法が既に決まっている
- スケール選択が主題（→ S1 Metron）
- 価値判断が主題（→ S4 Praxis）

---

## Precondition Check（発動前確認）

> **出力必須**: 以下を明示的に述べてから本処理に入る

スキル発動時に以下を**列挙出力**すること（形骸化防止）:

1. **読み込み済みファイル**: [対象モジュールのファイルリスト]
2. **上流からの入力**: [O2 Boulēsis / O4 Energeia からの入力、または「なし」]
3. **類似実装の有無**: [既存の方法設計参照先、または「なし」]

> [!CAUTION]
> 上記を出力せずに本処理に入った場合、**Precondition 違反**

---

## Core Function

**役割:** 認知の戦略を決定する

| 項目 | 内容 |
|------|------|
| **生成規則** | Flow × Function |
| **本質** | 認知をどの方法で行うかの配置 |
| **位置** | L2 S-series（様態層） |

---

## Processing Logic

```
┌─ 方法選択の必要性を検出
│
├─ Phase 1: 現在の方法確認
│  └─ 現在 Explore か Exploit か
│
├─ Phase 2: 適切な方法判断
│  ├─ 新しい可能性が必要？ → Explore 選択
│  └─ 確実な成果が必要？ → Exploit 選択
│
└─ Phase 3: 方法適用
   └─ 選択した方法で認知を実行
```

---

## Explore/Exploit の具体例

| 方法 | 認知活動 | 例 |
|------|----------|-----|
| **Explore** | 新規調査、実験、発見 | 技術調査、プロトタイプ作成 |
| **Exploit** | 既存活用、最適化、確実実行 | ベストプラクティス適用、リファクタリング |

---

## 上流・下流関係

| 方向 | 対象 | 関係 |
|------|------|------|
| **上流** | O2 Boulēsis, O4 Energeia | 本質から様態へ（意志・行為の方法化） |
| **下流** | H2 Pistis | 様態から傾向へ（方法化された確信） |
| **下流** | P2 Hodos | 様態から条件へ（方法化された経路） |

---

## X-series 接続

| X | 接続先 | 意味 |
|---|--------|------|
| **X-OS** | ← O-series | 本質から様態へ |
| **X-SH** | → H-series | 様態から傾向へ |
| **X-SP** | → P-series | 様態から条件へ |

---

## Micro 実現

| 層 | 実現手段 | 参照 |
|----|----------|------|
| **Micro** | /plan workflow | [plan.md](file:///home/laihuip001/oikos/.agent/workflows/plan.md) |

/plan は「戦略設計」であり、S2 Mekhanē の Micro 実現と見なせる。

---

## Edge Cases / Failure Modes

### ⚠️ Failure 1: 過度な Explore

**症状**: 常に新しいことを追求し、完成しない  
**対処**: Exploit フェーズを強制的に設定

### ⚠️ Failure 2: 過度な Exploit

**症状**: 既存手法に固執し、改善しない  
**対処**: 定期的な Explore 時間を確保

### ⚠️ Failure 3: Explore-Exploit 同時実行

**症状**: どちらも中途半端  
**対処**: フェーズを明確に分離

### ✓ Success Pattern

**事例**: 「調査（Explore）→ 決定 → 実装（Exploit）」の順序

---

## Output Format

```json
{
  "selected_method": "Explore | Exploit",
  "rationale": "選択理由",
  "strategy": "具体的な戦略説明",
  "delegate_to": "H2 Pistis | P2 Hodos"
}
```

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **上流** | O2 Boulēsis | 意志の方法化 |
| **上流** | O4 Energeia | 行為の方法化 |
| **下流** | H2 Pistis | 方法化された確信 |
| **下流** | P2 Hodos | 方法化された経路 |
| **X接続** | X-OS, X-SH, X-SP | 層間従属 |

---

*参照: [schema.md](file:///home/laihuip001/oikos/hegemonikon/kernel/schema.md)*  
*バージョン: 2.1.0 (2026-01-27)*
