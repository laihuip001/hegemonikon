---
doc_id: "OUSIA_SERIES"
version: "2.3.0"
tier: "KERNEL"
status: "CANONICAL"
created: "2026-01-24"
updated: "2026-02-01"
lineage: "FEP 'A Beautiful Loop' (2026-01-28 調査) → O1 recursive self-evidencing 追加"
extends:
  axioms: [L0.FEP, L1.Flow, L1.Value]
  generation: "L1 × L1"
---

> **Kernel Doc Index**: [axiom_hierarchy](axiom_hierarchy.md) | [ousia](ousia.md) ← 📍 | [schema](schema.md)

# Οὐσία (Ousia): 本質定理群

> **「認知の本質的機能」**

---

## 概要

| 項目 | 内容 |
|------|------|
| **シリーズ記号** | O |
| **定理数** | 4 |
| **生成規則** | L1 (核心) × L1 (核心) |
| **役割** | 本質的機能の定義 |

---

## 生成原理

```
L1 核心公理: Flow (I/A), Value (E/P)
    ×
L1 核心公理: Flow (I/A), Value (E/P)
    ↓
O-series: 2 × 2 = 4 定理
```

---

## 定理一覧

| ID | 名称 | 生成 | 意味 |
|----|------|------|------|
| O1 | **Noēsis** (Νόησις) | I × E | 認識推論 |
| O2 | **Boulēsis** (Βούλησις) | I × P | 意志推論 |
| O3 | **Zētēsis** (Ζήτησις) | A × E | 探索行動 |
| O4 | **Energeia** (Ἐνέργεια) | A × P | 実用行動 |

---

## 各定理の詳細

### O1: Noēsis (認識)

> **「世界を理解するための推論 — Recursive Self-Evidencing」**

- I (推論) × E (認識)
- 知識獲得のための思考
- **Recursive Self-Evidencing**: 予測誤差を最小化しながら、自己のモデル（信念）を再帰的に更新・証明するループ
- 例: 分析、調査、理論構築、前提破壊による再構築

> **FEP 対応**: Prior belief P(s) の更新。Phantasia（表象）をVariational parameters として処理し、観測との整合性を最大化する。

### O2: Boulēsis (意志)

> **「目的を定めるための推論」**

- I (推論) × P (実用)
- 目標設定、意思決定
- 例: 計画立案、優先順位決定

### O3: Zētēsis (探求)

> **「知識を得るための行動」**

- A (行為) × E (認識)
- 情報収集、調査活動
- 例: 検索、実験、観察

### O4: Energeia (活動)

> **「目的を達成するための行動」**

- A (行為) × P (実用)
- 目標達成のための実行
- 例: 実装、製造、配信

---

## 実装詳細

### 実現構造

```
定理群の実現手段 = Scale 公理 (L1.5: Micro ↔ Macro)

O-series 実現:
├─ Micro: .agent/workflows/ (即時的・セッション内)
└─ Macro: mekhane/ (永続的・インフラ)
```

### O1: Noēsis — 実装

| 項目 | 内容 |
|------|------|
| **発動条件** | `/noe` / 根本的行き詰まり / パラダイム転換 |
| **入力** | 問い Q |
| **出力** | 構造化知見（JSON形式、信頼度付き） |
| **Micro 実現** | [/noe](file:///home/makaron8426/oikos/.agent/workflows/noe.md) — 5フェーズ思考 |
| **Macro 実現** | (将来) mekhane/noesis/ — 知見蓄積・パターン学習 |
| **使用モジュール** | T3 (自問), T4 (判断), T7 (検証) |

### O2: Boulēsis — 実装

| 項目 | 内容 |
|------|------|
| **発動条件** | `/bou` / 作業一段落 / 方向性の迷い |
| **入力** | 領域（任意） |
| **出力** | 優先順位付き目標リスト + 次のアクション |
| **Micro 実現** | [/bou](file:///home/makaron8426/oikos/.agent/workflows/bou.md) — 6フェーズ意志明確化 |
| **Macro 実現** | (将来) mekhane/boulesis/ — 目標履歴・価値関数更新 |
| **使用モジュール** | — (純粋思考) |

### O3: Zētēsis — 実装

| 項目 | 内容 |
|------|------|
| **発動条件** | `/zet` / 不確実性検出 (U > 0.6) |
| **入力** | 調査テーマ |
| **出力** | 調査依頼書（深掘り版） |
| **Micro 実現** | [/zet](file:///home/makaron8426/oikos/.agent/workflows/zet.md) — 調査依頼書生成 |
| **Macro 実現** | mekhane/anamnesis/collectors/ — 外部情報収集 |
| **使用モジュール** | T5 (探索) |

### O4: Energeia — 実装

| 項目 | 内容 |
|------|------|
| **発動条件** | `/ene` / `y` (計画承認) / /bou 完了後 |
| **入力** | 承認済み計画 or 明確な意志 |
| **出力** | 成果物 + 検証結果 + コミット提案 |
| **Micro 実現** | [/ene](file:///home/makaron8426/oikos/.agent/workflows/ene.md) — 6フェーズ実行 |
| **Macro 実現** | mekhane/ergasterion/ — ファクトリ・プロトコル |
| **使用モジュール** | T6 (実行), T2 (判断) |

### O-series 連携図

```
O1 Noēsis（認識）
  └→ 「何が真実か」を問う
       ↓
O2 Boulēsis（意志）
  └→ 「何を望むか」を問う
       ↓
O3 Zētēsis（探求）
  └→ 「何を問うか」を調べる
       ↓
O4 Energeia（行為）
  └→ 「何をするか」を実行する
```

---

## X-series 接続

| X | 接続 | 意味 |
|---|------|------|
| X-OS | → S-series | 本質から様態へ |
| X-OH | → H-series | 本質から傾向へ |

---

## 関連ドキュメント

- [schema.md](schema.md) — S-series（下流）

---

*Ousia: アリストテレス形而上学における「本質・存在」*
