---
description: O1 Noēsis（深い認識・直観）を発動する最深層思考ワークフロー。5フェーズで前提破壊・ゼロ設計・GoT分析を実行。
hegemonikon: O1 Noēsis
version: "5.0"
lcm_state: stable       # draft | beta | stable | deprecated
derivatives: [nous, phro, meta, separate, align, metalearning]
trigonon:
  series: O
  type: Pure
  theorem: O1
  coordinates: [I, E]  # Flow=Internality, Value=Epistemic
  bridge: [S, H]       # via C1 Flow
  anchor_via: []        # Pure has no anchor (is the anchor)
  morphisms:
    ">>S": [/met, /mek, /sta, /pra]
    ">>H": [/pro, /pis, /ore, /dox]
cognitive_algebra:
  "+": 詳細分析（各フェーズで3倍の出力）
  "-": 要点分析（結論+理由1つのみ、5行以内）
  "*": メタ分析（分析の前提を問い直す）
---

# /noe: 最深層思考ワークフロー (Noēsis)

> **Hegemonikón**: O1 Noēsis（深い認識・直観）
> **目的**: 直観的認識、前提破壊、0からの再構築
> **発動条件**: 根本的な行き詰まり、パラダイム転換が必要な時
>
> **制約**: STEP 0 (SKILL.md 読込) を完了してから PHASE に進むこと。最終出力は必ずファイル保存すること。

---

## サブモジュール

| ファイル | 内容 |
|----------|------|
| [modes.md](noe/modes.md) | 派生モード (nous/phro/meta/separate/align/metalearning) |

---

## 発動条件

| トリガー | 説明 |
|:---------|:-----|
| `/noe` | 最深層思考を開始（派生自動選択） |
| `/noe [問い]` | 特定の問いで最深層思考 |
| `/noe --derivative=nous` | 強制的に nous モード |
| `/noe --derivative=phro` | 強制的に phro モード |
| `/noe --derivative=meta` | 強制的に meta モード |
| `/noe --mode=council` | 偉人評議会モード (旧 `/syn`) |

---

## 派生モード

> 詳細: [noe/modes.md](noe/modes.md)

| 派生 | 適用場面 | 出力特性 |
|:-----|:---------|:---------|
| **nous** | 抽象的・原理探求 | 普遍原理 |
| **phro** | 具体的・実践的 | 状況適応的判断 |
| **meta** | 信頼性疑問・自己反省 | 認識の認識 |
| **separate** | 問題分離 | 部分問題リスト |
| **align** | 整合・調整 | 整合状態 |
| **metalearning** | 学習の学習 | 学習戦略 |

---

## 処理フロー

1. **STEP 0**: SKILL.md を view_file で読み込む（必須）
2. **PHASE 0**: 派生選択（Derivative Selection）
3. **PHASE 0.5**: 盲点カテゴリチェック
4. **PHASE 1**: 前提掘出（Premise Excavation）
5. **PHASE 2**: ゼロ設計（Zero-shot Restructuring）+ 発想モード
6. **PHASE 3**: 分析深化（Analytical Deepening, GoT）
7. **PHASE 4**: 自己検証（Self-Verification）
8. **PHASE 5**: メタ認知出力（Metacognitive Output）
9. 最終出力: 構造化知見 → ファイル保存

---

## PHASE 2 発想モード (AI Zen 消化)

PHASE 2 のゼロ設計時に思考を拡散させるトリガー:

| モード | 説明 | プロンプト例 |
|:-------|:-----|:-------------|
| Analogy | 動物から連想 | 「この問題を解決する生物の戦略は？」 |
| 10x | 10倍の目標 | 「目標を10倍にしたら？」 |
| Gap | 隙のあるアイデア | 「未成熟なたたき台を出す」 |
| Art | 芸術からの示唆 | 「この問題を表すアートは？」 |
| Random | ランダム組合せ | 「無関係な単語と組み合わせ」 |
| Alien | 異質の取入れ | 「異なる分野のアプローチ」 |

---

## 派生選択ロジック

> 派生未指定時、問題の特性から最適な派生を提案する。

```python
from mekhane.fep.derivative_selector import select_derivative

result = select_derivative("O1", problem_context)
# → nous: 抽象度が高い問題
# → phro: 文脈依存度が高い問題
# → meta: 反省必要度が高い問題
```

---

## 自動提案の出力形式

| 項目 | 内容 |
|:-----|:-----|
| 問い | {user_question} |
| 推奨派生 | {derivative} ({confidence}%) |
| 理由 | {rationale} |
| 代替 | {alternatives} |
| 確認 | このまま実行 / 代替 / キャンセル |

---

## Artifact 自動保存

出力先: `~/oikos/mneme/.hegemonikon/workflows/noe_<topic>_<date>.md`

完了時の出力:

- 保存先パス、要約1行、X-series 推奨次ステップを表示

---

## X-series 推奨次ステップ

Noēsis 完了後の推奨遷移:

| コマンド | 遷移 | 説明 |
|:---------|:------|:-----|
| /s | X-O1S1 | 認識→スケール |
| /dia | X-O1A2 | 認識→検証 |
| /pro | X-O1H1 | 認識→初期傾向 |
| (完了) | — | このまま終了 |

---

## Hegemonikón Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| O1 Noēsis | /noe | v5.1 Ready |

> **制約リマインダ**: SKILL.md 読込 (STEP 0) → 派生選択 (PHASE 0) → 5 Phase 実行。順序を守ること。

---

*v5.1 — FBR 適用 (2026-02-07)*
