---
description: S2 Mekhanē（方法配置）を発動し、スキル/ワークフローを生成・診断する。tekhne-maker 統合。
hegemonikon: Schema
modules: [S2]
skill_ref: ".agent/skills/schema/s2-mekhane/SKILL.md"
triggers: ["スキルを作る", "ワークフローを作る", "プロンプト", "mekhane", "ccl"]
version: "7.1"
lcm_state: stable       # draft | beta | stable | deprecated
lineage: "v7.0 + Functional Beauty Redesign → v7.1"
derivatives: [comp, inve, adap, model, simulation, observability, substitute, yagni, dry, nudge, visual, manual]
trigonon:
  series: S
  type: Mixed
  theorem: S2
  coordinates: [I, Function]
  bridge: [H, K]
  anchor_via: [O, P]
  morphisms:
    ">>H": [/pro, /pis, /ore, /dox]
    ">>K": [/euk, /chr, /tel, /sop]
cognitive_algebra:
  "+": "詳細生成：全ステップ展開、設計根拠記載"
  "-": "高速生成：最小限の構造、すぐ使える形"
  "*": "メタ生成：生成プロセス自体を問う"
sel_enforcement:
  "+":
    minimum_requirements:
      - "全 STEP (0-7) を展開して出力"
      - "設計根拠: 各選択の WHY を記載"
      - "Pre-Mortem: 失敗シナリオを1つ以上"
      - "CCL 複雑度: ポイント計算を明示"
  "-":
    minimum_requirements:
      - "最小構造のみ、即座に使える形で出力"
submodules:
  - basic-modes.md
  - engineering-modes.md
  - advanced-modes.md
  - output-modes.md
  - ccl-generation.md
  - artifact-rules.md
---

# /mek — 方法配置ワークフロー (Mekhane)

> S2 Mekhanē — スキル・ワークフローの生成、診断、改善。
> **正本**: [tekhne-maker SKILL.md](file:///home/makaron8426/oikos/hegemonikon/mekhane/ergasterion/tekhne/SKILL.md)

## Constraints

- 実行前に SKILL.md を必ず読み込む（省略禁止）
- 出力はテーブル形式で構造化する。装飾よりも情報構造を優先する
- 生成物は「初版」として扱い、`/dia-` でレビューを推奨する

---

## Sub-modules

| モジュール | 内容 |
|:-----------|:-----|
| [basic-modes.md](mek/basic-modes.md) | comp, inve, adap, model, simulation |
| [engineering-modes.md](mek/engineering-modes.md) | yagni, dry, observability, substitute, nudge |
| [advanced-modes.md](mek/advanced-modes.md) | reverse, constitutional, yaml, multi |
| [output-modes.md](mek/output-modes.md) | visual, manual |
| [ccl-generation.md](mek/ccl-generation.md) | CCL生成モード (4層フォールバック) |
| [artifact-rules.md](mek/artifact-rules.md) | SE原則、計算コスト、使用例 |

---

## Cognitive Algebra

| Operator | Meaning | Output |
|:---------|:--------|:-------|
| `/mek+` | Deepening | 詳細生成: 全ステップ展開、設計根拠 |
| `/mek-` | Reduction | 高速生成: 最小限構造、即座に使える |
| `/mek*` | Expansion | メタ生成: 「この生成方法は正しいか」 |

---

## CCL 複雑度ポイント制

> **参照**: [operators.md](file:///home/makaron8426/oikos/hegemonikon/ccl/operators.md)

生成した CCL のポイントを計算し、帯域内に収める:

| 帯域 | pt | 用途 |
|:-----|:---|:-----|
| Standard | 15-30pt | `/mek` |
| Enhanced | 30-45pt | `/mek+` |
| Warning | 60pt+ | 分割推奨 |

| pt | 演算子 |
|:--:|:-------|
| 1 | `+`, `-`, `_` |
| 2 | `>>`, `E:{}`, `let` |
| 3 | `^`, `√`, `'`, `∂`, `E[]`, `*` |
| 4 | `~`, `Σ`, `V[]`, `I:[]{}` |
| 5 | `\`, `∫`, `F:[]{}` |
| 6 | `!`, `W:[]{}` |
| +4/+10/+18 | ネスト Lv1/Lv2/Lv3 |

---

## Derivatives

| 派生 | 適用場面 | 生成特性 |
|:-----|:---------|:---------|
| comp | 既存部品を組み立てる | 組合せ、統合、合成 |
| inve | 新規に創出する | 発明、革新、着想 |
| adap | 既存を適応させる | 調整、カスタマイズ、最適化 |
| lit | プロンプト教養を教える | 言葉遣い解説、履歴フィードバック |
| visual | 視覚的成果物を生成 | 画像、モックアップ、インフォグラフィック |
| manual | 作業マニュアルを生成 | Gemini/Jules向け補完防止手順書 |

### 自動モード選択

`/mek` のみで実行した場合、要件から自動的に派生モードを提案する:

| フィールド | 内容 |
|:-----------|:-----|
| 要件 | {生成要件} |
| 推奨派生 | {derivative} ({confidence}%) |
| 理由 | {rationale} |
| 代替 | {alternatives} |
| 確認 | このまま {derivative} で生成？ [y/代替/n] |

```python
from mekhane.fep.derivative_selector import select_derivative
result = select_derivative("S2", "新しいワークフローを作りたい")
```

---

## Triggers

| トリガー | 説明 |
|:---------|:-----|
| `/mek` | Hegemonikon Mode (デフォルト) — 定理体系に馴染む生成 |
| `/mek vulg` | 俗モード — 例外的に体系外の生成が必要な場合のみ |
| `/mek [要件]` | 指定要件でスキル生成 |
| `/mek diagnose [file]` | 既存プロンプトを診断 |
| `/mek improve [file]` | 既存プロンプトを改善 |
| `/mek ccl "意図"` | CCL生成モード — 自然言語から CCL v2.0 式を生成 |

---

## Pre-requisites

SKILL.md を必ず読み込んでから処理を開始する:

```text
1. view_file: /home/makaron8426/oikos/hegemonikon/mekhane/ergasterion/tekhne/SKILL.md
2. Operating Modes セクション確認
3. 要件に応じたモード選択
```

参照ファイル（生成品質に直結するため省略禁止）:

| ファイル | 目的 |
|:---------|:-----|
| references/archetypes.md | Archetype 選択根拠 |
| references/quality-checklist.md | 品質基準 |
| references/wargame-db.md | 失敗シナリオ |

パス: `/home/makaron8426/oikos/hegemonikon/mekhane/ergasterion/tekhne/references/`

---

## Modes

| モード | トリガー | 出力 |
|:-------|:---------|:-----|
| Hegemonikon | `/tek hege` | 定理体系に馴染むスキル/ワークフロー |
| Generate (Skill) | `/tek [要件]` | SKILL.md |
| Generate (Workflow) | Interactive → Workflow | workflow.md |
| Diagnose | `/tek diagnose` | スコア表 + 改善案 |
| Improve | `/tek improve` | 差分のみ提示 |
| SAGE | `/tek sage` | XML/MD ハイブリッド |
| Prompt-Lang | `/tek pl` | .prompt ファイル |
| Reverse | `/mek reverse` | 出力→プロンプト逆生成 |
| Constitutional | `/mek constitution` | 原則優先度付き生成 |
| YAML | `/mek yaml` | YAML+MD ハイブリッド |
| Multi-expert | `/mek multi` | 並列専門家対話 |

---

## Process

1. **STEP 0**: SKILL.md を view_file で読み込む（必須）
2. **STEP 1**: モード判定 (1分)
   - 明示的指定がない場合 → Generate
   - diagnose/improve → 対象ファイル読み込み
3. **STEP 1.5**: Information Absorption Layer (3分)
   - Q1: Creator が「当たり前」と思っている知識は何か？
   - Q2: 対象ドメインの暗黙の前提は何か？
   - Q3: 過去の関連 KI/Handoff は何か？
   - 背景情報3倍則: 指示トークン × 3 = 必要な背景情報トークン
   - 背景情報が不十分な場合、`/zet` で追加調査
4. **STEP 2**: M1 OVERLORD — Semantic Audit (2分)
   - 曖昧性検出、Hidden Agenda 抽出
5. **STEP 3**: M2 RECURSIVE_CORE — 3層処理 (5分)
   - Layer 1: EXPANSION (拡散)
   - Layer 2: CONFLICT (対立) — Fail Fast 原則
     - Q1: この生成物が失敗するとしたら、なぜ？
     - Q2: 最悪のケースは何か？
     - Q3: その失敗を今の時点で回避できるか？
     - 答えられない場合、生成を中断して再設計
   - Layer 3: CONVERGENCE (収束)
6. **STEP 4**: M3 ARCHETYPE_ENGINE — アーキタイプ選択 (2分)
   - 5 Diagnostic Questions
   - Precision / Speed / Autonomy / Creative / Safety
7. **STEP 5**: M4 RENDERING_CORE — 出力生成 (5分)
   - BLUF Rule + Visual Logic Rule
8. **STEP 6**: M5 QUALITY_ASSURANCE — 検証 (2分)
   - Pre-Mortem Simulation + WARGAME_DB Check
9. **STEP 7**: SE反復原則 — 初版確認
   - `/dia-` クイックレビュー推奨
   - `/dia+` 詳細レビュー
10. **最終出力**: 成果物 → ファイル保存

---

---

## @complete: 射の提案 (暗黙発動 L1)

> WF完了時、`/x` 暗黙発動プロトコルにより射を提案する。
> 計算ツール: `python mekhane/taxis/morphism_proposer.py mek`

```
/mek 完了 → @complete 発動
→ 結果に確信がありますか？ (Y: Anchor優先 / N: Bridge優先 / 完了)
```

## Hegemonikon Status

| Module | Workflow | Skill (正本) | Status |
|:-------|:---------|:-------------|:-------|
| tekhne-maker | /tek | [SKILL.md](file:///home/makaron8426/oikos/hegemonikon/mekhane/ergasterion/tekhne/SKILL.md) | v5.0 Ready |

---

## Post-Check (環境強制)

> **`+` モード時のみ自動発動。** 出力が sel_enforcement の minimum_requirements を満たすか検証。

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python scripts/wf_postcheck.py --wf mek --mode "+" --text "$MEK_OUTPUT"
```

> FAIL 時は不足を補完してから Creator に提示。PASS するまでループ。

---

## Reminder

- SKILL.md を読み込まずに生成を開始しない
- 出力はテーブル形式。装飾より情報構造
- 生成物は初版。`/dia-` でレビューを推奨

*v7.1 — Functional Beauty Redesign (2026-02-07)*
