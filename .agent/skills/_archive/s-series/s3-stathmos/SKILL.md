---
# === Metadata Layer (v2.1) ===
id: "S3"
name: "Stathmos"
greek: "Σταθμός"
category: "modal-theorem"
description: >
  Applies the S3 Stathmos schema from the Hegemonikón framework for value baseline selection.
  Use this skill when the user needs to set evaluation criteria, establish reference points,
  or determine the scale for value judgments (Micro detail vs Macro strategic).
  Triggers: 基準, baseline, reference point, evaluation criteria, benchmark, anchor.

# v2.1 生成規則
generation:
  layer: "L2 S-series (Schema)"
  formula: "Value (E/P) × Scale (M/M)"
  result: "スケール価値 — 基点での配置"
  axioms:
    - L1.2 Value (E/P): 認識/実用の選択
    - L1.5.1 Scale (M/M): Micro/Macro の選択

# 発動条件
triggers:
  - value scale decision
  - evaluation granularity
  - reference point selection
  - baseline setting

# キーワード
keywords:
  - baseline
  - reference
  - anchor
  - standard
  - criterion
  - benchmark

# 使用条件
when_to_use: |
  価値判断の「粒度」を決定する必要がある時。
  詳細な価値分析（Micro）か大局的価値判断（Macro）かを選ぶ時。

when_not_to_use: |
  - 基準が既に決まっている場合
  - 行動の粒度選択が必要な時（→ S1 Metron）

# 関連 (v2.1)
related:
  upstream:
    - "O1 Noēsis"
    - "O3 Zētēsis"
  downstream:
    - "H3 Orexis"
    - "P3 Trokhia"
  x_series: ["X-OS", "X-SH", "X-SP"]
  micro: null
  macro: null

version: "2.1.0"
---

# S3: Stathmos (Σταθμός) — 基点

> **生成規則:** Value (E/P) × Scale (M/M) = スケール価値
>
> **問い**: どの基準点から価値を配置するか？
>
> **役割**: 価値判断の「粒度」を決定する

---

## When to Use（早期判定）

### ✓ Trigger となる条件

- 価値判断のスケール選択が必要な時
- 評価の粒度を決める必要がある
- 基準点・アンカーの設定
- ベースラインの決定

### ✗ Not Trigger

- 基準が既に決まっている
- 行動のスケール選択が主題（→ S1 Metron）
- 方法選択が主題（→ S2 Mekhanē）

---

## Core Function

**役割:** 価値判断の粒度を決定する

| 項目 | 内容 |
|------|------|
| **生成規則** | Value × Scale |
| **本質** | 価値評価をどのレベルで行うかの配置 |
| **位置** | L2 S-series（様態層） |

---

## Processing Logic

```
┌─ 価値スケール選択の必要性を検出
│
├─ Phase 1: 現在の評価スケール確認
│  └─ 現在 Micro か Macro か
│
├─ Phase 2: 適切なスケール判断
│  ├─ 詳細な評価が必要？ → Micro 選択
│  └─ 大局的判断が必要？ → Macro 選択
│
└─ Phase 3: 基準点設定
   └─ 選択したスケールで評価基準を設定
```

---

## Micro/Macro 価値評価の具体例

| スケール | 評価活動 | 例 |
|----------|----------|-----|
| **Micro** | 詳細な品質チェック、項目別評価 | コードレビュー、チェックリスト評価 |
| **Macro** | 全体的な価値判断、戦略的評価 | ROI 評価、プロジェクト価値判断 |

---

## 上流・下流関係

| 方向 | 対象 | 関係 |
|------|------|------|
| **上流** | O1 Noēsis, O3 Zētēsis | 本質から様態へ（認識・探求の価値スケール化） |
| **下流** | H3 Orexis | 様態から傾向へ（スケール化された欲求） |
| **下流** | P3 Trokhia | 様態から条件へ（スケール化された軌道） |

---

## X-series 接続

| X | 接続先 | 意味 |
|---|--------|------|
| **X-OS** | ← O-series | 本質から様態へ |
| **X-SH** | → H-series | 様態から傾向へ |
| **X-SP** | → P-series | 様態から条件へ |

---

## Edge Cases / Failure Modes

### ⚠️ Failure 1: 基準の不在

**症状**: 何を基準に評価すべきかわからない  
**対処**: 明示的に基準を設定

### ⚠️ Failure 2: 過度に厳密な基準

**症状**: 全てを Micro で評価し、進まない  
**対処**: 重要度に応じてスケールを調整

### ✓ Success Pattern

**事例**: 「重要な決定は Macro で → 実装詳細は Micro で」

---

## Output Format

```json
{
  "selected_scale": "Micro | Macro",
  "baseline": "設定した基準点",
  "evaluation_criteria": ["評価基準1", "評価基準2"],
  "delegate_to": "H3 Orexis | P3 Trokhia"
}
```

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **上流** | O1 Noēsis | 認識の価値スケール化 |
| **上流** | O3 Zētēsis | 探求の価値スケール化 |
| **下流** | H3 Orexis | スケール化された欲求 |
| **下流** | P3 Trokhia | スケール化された軌道 |
| **X接続** | X-OS, X-SH, X-SP | 層間従属 |

---

*参照: [schema.md](file:///home/laihuip001/oikos/hegemonikon/kernel/schema.md)*  
*バージョン: 2.1.0 (2026-01-27)*
