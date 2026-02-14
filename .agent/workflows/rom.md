---
description: セッション中のコンテキストを構造化・蒸留して外部ファイル（ROM）に保存する。RAM→ROM の焼付けワークフロー。
hegemonikon: Schema, Hormē, Perigraphē
modules: [S1, H1, H2, H4, P1]
version: "1.0"
lcm_state: beta
derivatives: [rom-, rom, rom+]
cognitive_algebra:
  "+": "RAG最適化出力。Extended MD + XML構造化 + AI参照ガイド埋込み"
  "-": "即保存。5行要約 + 決定事項リスト"
  "*": "メタ分析。なぜ今これを ROM に焼く必要があるか"
sel_enforcement:
  "+":
    description: "MUST execute full distillation pipeline with RAG optimization"
    minimum_requirements:
      - "Frontmatter 完全構築 必須"
      - "意味タグ (DEF/FACT/RULE/DECISION/DISCOVERY) 付与 必須"
      - "AI参照ガイド (HTMLコメント) 埋込み 必須"
      - "品質チェック (/pis) 必須"
  "-":
    description: "MAY provide minimal context snapshot"
    minimum_requirements:
      - "5行以内の要約"
      - "決定事項リスト"
  "*":
    description: "MUST meta-analyze: why externalize now?"
    minimum_requirements:
      - "ROM 化する理由のメタ分析"
anti_skip: enabled
related:
  adjunction: "/bye (全体圧縮) の部分関手。/rom は選択的射影"
  dual: "/boot (ROM読込) — Write⊣Read"
  x_series:
    - "X-SH: S1 → H2 (方針→確信度)"
    - "X-PK: P1 → K (場→文脈)"
ccl_signature: "/pro_/kho{ctx}_/s-{distill}_/pis_/dox{ROM}"
category_theory:
  core: "射影関手 π: Ses → Rom (Rom ⊂ Mem)"
  insight: "/bye = R: Ses → Mem (全体圧縮)。/rom = π: Ses → Rom (選択的射影)。RAM↔ROMの対比。"
---

# /rom: コンテキスト ROM 焼付けワークフロー

> **Hegemonikón**: S1 Theōria (方向性) + P1 Khōra (場) + H2 Pistis (確信)
> **圏論的正体**: 射影関手 π: Ses → Rom — セッション状態の選択的射影
> **目的**: セッション中に RAM（コンテキストウィンドウ）から ROM（外部ファイル）へ、選択的にコンテキストを蒸留・保存する
>
> **哲学**: RAM は揮発性。ROM は永続性。Context ROX（LS 50KB制限）対策として、
> 「今の文脈」を構造化して外部に焼き付け、コンテキストの寿命を延ばす。
>
> **制約**: 全てを焼くのは `/bye`。`/rom` は「選択と蒸留」。何を残し何を捨てるかの判断が核心。

---

## 対比構造: RAM ↔ ROM

```
RAM = コンテキストウィンドウ (揮発性、50KB制限)
ROM = 外部ファイル (永続性、検索可能)

/rom  = Write: RAM → ROM  (選択的射影・蒸留)
/boot = Read:  ROM → RAM  (復元・展開)
/bye  = Full:  RAM → Mem  (全体圧縮)
```

| 概念 | 操作 | スコープ |
|:-----|:-----|:---------|
| `/rom` | 選択的書出し | セッション中の任意タイミング |
| `/bye` | 全体圧縮 | セッション終了時 |
| Savepoint | 軽量チェックポイント | 🟡→🟠 遷移時 |
| Handoff | 引継ぎ文書 | `/bye` の成果物 |
| ROM | 蒸留済みナレッジ | `/rom` の成果物 |

---

## 認知機能マッピング (CCL)

**CCL**: `@rom = /pro_/kho{ctx}_/s-{distill}_/pis_/dox{ROM}`

| # | CCL | 認知機能 | Series | なぜ必要か |
|:--|:----|:---------|:-------|:----------|
| 1 | `/pro` | H1 前感情 | H-series | 「今何が重要か」の直感的判断。蒸留対象の初期選定 |
| 2 | `/kho{ctx}` | P1 文脈場 | P-series | 現在のコンテキストを場として展開・可視化 |
| 3 | `/s-{distill}` | S1 方向性 | S-series | 蒸留方針の決定（何を残し何を捨てるか） |
| 4 | `/pis` | H2 確信度 | H-series | 蒸留結果の品質・信頼度を評価 |
| 5 | `/dox{ROM}` | H4 信念記録 | H-series | 外部ファイルに永続化 |

---

## 発動条件

| トリガー | 説明 |
|:---------|:-----|
| `/rom [対象]` | 指定した対象を ROM に焼く |
| `/rom` (対象なし) | 現在のセッション全体から蒸留対象を自動選定 |
| 「コンテキストを保存して」 | 自然言語トリガー |
| 「ROM に焼いて」 | メタファートリガー |
| Context Rot 検知時 | BC-18 の 🟡→🟠 遷移で自動提案 |

---

## 処理フロー

// turbo-all

### Phase 0: コンテキスト棚卸し (/pro)

**目的**: 「今何が重要か」を直感的に判断し、蒸留対象を選定する

1. **Intent-WAL との照合**: セッション開始時の目的と現在地の比較
2. **蓄積情報のカテゴリ分類**:

| カテゴリ | 内容 | 優先度 |
|:---------|:-----|:-------|
| **decisions** | 確定した判断・設計決定 | 🔴 必ず保存 |
| **discoveries** | 新たに発見した事実・知見 | 🔴 必ず保存 |
| **context** | 背景情報・前提条件 | 🟡 選択的 |
| **artifacts** | 中間成果物・生成コード | 🟡 選択的 |
| **failures** | 失敗した試行・却下案 | 🟢 重要なもののみ |

1. **保存対象の最終リスト作成**

**出力**:

```
📋 ROM 棚卸し:
  [DECISION] {決定事項1}
  [DISCOVERY] {発見1}
  [CONTEXT] {背景情報1}
  → ROM 化対象: {N}件
```

---

### Phase 1: 蒸留方針決定 (/kho + /s-)

**目的**: コンテキストの場を展開し、蒸留方針を決める

1. **コンテキストの構造分析**:
   - 関連する WF/Skill/定理を特定
   - 情報間の依存関係をマッピング
2. **蒸留深度の決定** (派生に従う):

| 派生 | 深度 | テンプレート | 用途 |
|:-----|:-----|:-----------|:-----|
| `/rom-` | L1 | Snapshot | 即座にメモを残す。5行要約 + 箇条書き |
| `/rom` | L2 | Distilled MD | 構造化された蒸留。Frontmatter + 意味タグ |
| `/rom+` | L3 | RAG-Optimized | AI参照最適化。Extended MD + 検索拡張 + AI参照ガイド |

---

### Phase 2: 蒸留実行 (Distillation)

**目的**: 選定された情報を、派生に応じたテンプレートで圧縮・構造化する

#### /rom- テンプレート (Snapshot)

```markdown
---
rom_id: rom_{date}_{short_topic}
session_id: {conversation_id}
created_at: {YYYY-MM-DD HH:MM}
rom_type: snapshot
---
# {トピック}
{5行以内の高密度要約}
## 決定事項
- {decision_1}
- {decision_2}
## 次回アクション
- {action_1}
```

#### /rom テンプレート (Distilled MD)

```markdown
---
rom_id: rom_{date}_{short_topic}
session_id: {conversation_id}
created_at: {YYYY-MM-DD HH:MM}
rom_type: distilled
reliability: High | Medium | Low
topics: [keyword1, keyword2, ...]
exec_summary: |
  3行以内の高密度要約
---

# {トピック名} {#sec_01_topic}

> **[DECISION]** {確定した判断}

{蒸留された内容。冗長表現トリミング済み、固有名詞・数値・因果関係は100%保持}

> **[DISCOVERY]** {発見した事実}

{蒸留された内容}

> **[CONTEXT]** {背景情報}

{蒸留された内容}

## 関連情報
- 関連 WF: {/xxx}
- 関連 KI: {ki_name}
- 関連 Session: {session_id}

<!-- ROM_GUIDE
primary_use: {このROMの主な用途}
retrieval_keywords: {検索用キーワード}
expiry: {鮮度期限 or "permanent"}
-->
```

#### /rom+ テンプレート (RAG-Optimized)

Distilled MD テンプレートに加え:

1. **Semantic ID**: 全見出しに `{#sec_NN_slug .attributes}` 形式のIDを付与
2. **意味タグ強化**: `[DEF]`, `[FACT]`, `[RULE]`, `[CONFLICT]`, `[OPINION]` を全ブロックに付与
3. **検索拡張メタデータ**: 本文にないが検索されそうな同義語・略語・関連概念を生成
4. **AI参照ガイド** (HTMLコメント):

```html
<!-- AI_REFERENCE_GUIDE
primary_query_types:
  - "{想定される質問タイプ1}"
  - "{想定される質問タイプ2}"
answer_strategy: "{このROMから回答する際の戦略}"
confidence_notes: "{信頼度に関する注記}"
related_roms: ["{関連ROM_ID}"]
-->
```

1. **複雑な関係の可視化**: 循環依存や多分岐プロセスがある場合のみ Mermaid 図解

---

### Phase 3: 品質チェック (/pis)

**目的**: 蒸留結果の品質を評価する

| チェック項目 | 基準 |
|:------------|:-----|
| **情報保存率** | 決定事項・発見は100%保持されているか |
| **赤の他人基準** | このROMだけで文脈を理解できるか (BC-15) |
| **トークン効率** | 元のコンテキスト対比で十分に圧縮されているか |
| **検索性** | topics/keywords が適切で、後で見つけられるか |
| **鮮度情報** | source_date, reliability が正確か |

出力:

```
🔍 ROM 品質:
  情報保存率: {%}
  圧縮率: {元サイズ} → {ROMサイズ} ({比率})
  確信度: [確信: {%}] (SOURCE: {根拠})
```

---

### Phase 4: 焼付け (Write to ROM)

**目的**: 蒸留済みコンテンツを外部ファイルに保存する

1. **ファイル保存**:

```bash
# 保存先
~/oikos/mneme/.hegemonikon/rom/rom_{date}_{short_topic}.md
```

1. **Mnēmē 連携** (将来):
   - `anamnesis/cli.py` でインデックスに登録
   - ベクトル検索で `/boot` 時に自動浮上可能に

---

### Phase 5: コンテキスト解放

**目的**: ROM に焼いた情報を意識的に手放し、コンテキスト空間を確保する

1. **焼付け完了レポート**:

```
✅ /rom 完了
📄 ~/oikos/mneme/.hegemonikon/rom/{filename}
📊 圧縮: {元} → {ROM} ({比率})
🔓 コンテキスト解放: {解放した情報の要約}
⚡ 燃料メーター: ~{fuel}%
→ {推奨次ステップ}
```

1. **燃料メーター更新**: ROM化により実質的にコンテキストの有効利用率が改善

---

## 双対構造

| WF | 方向 | スコープ | タイミング |
|:---|:-----|:---------|:----------|
| `/rom` | RAM → ROM | 選択的 | セッション中 |
| `/bye` | RAM → Mem | 全体 | セッション終了 |
| `/boot` | Mem → RAM | 復元 | セッション開始 |

`/rom` は `/bye` の部分適用であり、`/boot` の部分入力を準備する。

---

## Context Rot との連携 (BC-18)

| 状態遷移 | /rom との関係 |
|:---------|:-------------|
| 🟢→🟡 | `/rom` を**提案** — 「重要な判断を ROM に焼きませんか？」 |
| 🟡→🟠 | `/rom` を**推奨** — Savepoint 代わりに構造化保存 |
| 🟠→🔴 | `/rom` + `/bye` を**強制** — 焼ける物は全て焼いて撤退 |

---

## Artifact 自動保存

**保存先**: `~/oikos/mneme/.hegemonikon/rom/rom_{date}_{short_topic}.md`

**ファイル命名規則**:

- `rom_` + 日付 `YYYY-MM-DD` + `_` + 短いトピック名（英語、snake_case）
- 例: `rom_2026-02-14_jules_eafp.md`, `rom_2026-02-14_axiom_hierarchy.md`

---

*v1.0 — 初版作成 (2026-02-14)*
