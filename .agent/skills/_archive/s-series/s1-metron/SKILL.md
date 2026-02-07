---
# === Metadata Layer (v2.1) ===
id: "S1"
name: "Metron"
greek: "Μέτρον"
category: "modal-theorem"
description: >
  Applies the S1 Metron schema from the Hegemonikón framework for scale selection.
  Use this skill when the user needs to choose between Micro (detailed) or Macro (holistic) 
  perspectives, adjust granularity, or decide zoom level for analysis.
  Triggers: スケール, granularity, micro vs macro, zoom, 粒度, level of detail.

# v2.1 生成規則
generation:
  layer: "L2 S-series (Schema)"
  formula: "Flow (I/A) × Scale (M/M)"
  result: "スケール流動 — 尺度での配置"
  axioms:
    - L1.1 Flow (I/A): 推論/行為の選択
    - L1.5.1 Scale (M/M): Micro/Macro の選択

# 発動条件
triggers:
  - scale decision required
  - micro vs macro choice
  - granularity selection
  - zoom level change

# キーワード
keywords:
  - scale
  - granularity
  - micro
  - macro
  - zoom
  - level

# 使用条件
when_to_use: |
  認知の「粒度」を決定する必要がある時。
  詳細分析（Micro）か全体把握（Macro）かを選ぶ時。

when_not_to_use: |
  - スケールが既に決まっている場合
  - 方法選択が必要な時（→ S2 Mekhanē）

# 関連 (v2.1)
related:
  upstream:
    - "O1 Noēsis"
    - "O3 Zētēsis"
  downstream:
    - "H1 Propatheia"
    - "P1 Khora"
  x_series: ["X-OS", "X-SH", "X-SP"]
  micro: null  # 個別 workflow なし
  macro: null  # 個別 mekhane なし

version: "2.1.0"
risk_tier: L0
reversible: true
requires_approval: false
risks:
  - "アーカイブ済みスキルの誤参照による古い手法の適用"
fallbacks: []
---

# S1: Metron (Μέτρον) — 尺度

> **生成規則:** Flow (I/A) × Scale (M/M) = スケール流動
>
> **問い**: どのスケールで認知を配置するか？
>
> **役割**: 認知の「粒度」を決定する

---

## When to Use（早期判定）

### ✓ Trigger となる条件

- スケール選択が必要な時
- Micro vs Macro の判断が必要
- 詳細度の調整が必要
- ズームイン/ズームアウトの判断

### ✗ Not Trigger

- スケールが既に決まっている
- 方法選択が主題（→ S2 Mekhanē）
- 価値判断が主題（→ S3 Stathmos）

---

## Core Function

**役割:** 認知の粒度を決定する

| 項目 | 内容 |
|------|------|
| **生成規則** | Flow × Scale |
| **本質** | 認知をどのレベルで行うかの配置 |
| **位置** | L2 S-series（様態層） |

---

## Processing Logic

```
┌─ スケール選択の必要性を検出
│
├─ Phase 1: 現在のスケール確認
│  └─ 現在 Micro か Macro か
│
├─ Phase 2: 適切なスケール判断
│  ├─ 詳細が必要？ → Micro 選択
│  └─ 全体把握が必要？ → Macro 選択
│
└─ Phase 3: スケール適用
   └─ 選択したスケールで認知を実行
```

---

## Micro/Macro の具体例

| スケール | 認知活動 | 例 |
|----------|----------|-----|
| **Micro** | 詳細分析、行ごとの検査 | コードレビュー、バグ調査 |
| **Macro** | 全体設計、アーキテクチャ | システム設計、戦略立案 |

---

## 上流・下流関係

| 方向 | 対象 | 関係 |
|------|------|------|
| **上流** | O1 Noēsis, O3 Zētēsis | 本質から様態へ（認識・探求のスケール化） |
| **下流** | H1 Propatheia | 様態から傾向へ（スケール化された反応） |
| **下流** | P1 Khora | 様態から条件へ（スケール化された空間） |

---

## X-series 接続

| X | 接続先 | 意味 |
|---|--------|------|
| **X-OS** | ← O-series | 本質から様態へ |
| **X-SH** | → H-series | 様態から傾向へ |
| **X-SP** | → P-series | 様態から条件へ |

---

## Edge Cases / Failure Modes

### ⚠️ Failure 1: スケール固定

**症状**: 常に同じスケールで考える  
**対処**: 意図的にスケールを変えてみる

### ⚠️ Failure 2: スケール振動

**症状**: Micro と Macro を行き来して収束しない  
**対処**: 一つのスケールで完了してから切り替え

### ✓ Success Pattern

**事例**: 「まず全体設計（Macro）→ 詳細実装（Micro）」の順序

---

## Output Format

```json
{
  "selected_scale": "Micro | Macro",
  "rationale": "選択理由",
  "current_context": "現在の認知対象",
  "delegate_to": "H1 Propatheia | P1 Khora"
}
```

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **上流** | O1 Noēsis | 認識のスケール化 |
| **上流** | O3 Zētēsis | 探求のスケール化 |
| **下流** | H1 Propatheia | スケール化された反応 |
| **下流** | P1 Khora | スケール化された空間 |
| **X接続** | X-OS, X-SH, X-SP | 層間従属 |

---

*参照: [schema.md](file:///home/makaron8426/oikos/hegemonikon/kernel/schema.md)*  
*バージョン: 2.1.0 (2026-01-27)*
