---
description: O1 Noēsis（深い認識・直観）を発動する最深層思考ワークフロー。7フェーズ (0-6) で圏論的普遍性を追求。
hegemonikon: O1 Noēsis
version: "6.1"
skill_ref: ".agent/skills/ousia/o1-noesis/SKILL.md"
lcm_state: stable
derivatives: [nous, phro, meta, separate, align, metalearning, scaffold]
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
category_theory:
  functor: "F: Cat → Noe — 圏論の圏から /noe の圏への完全な関手"
  kalon: "Kalon する = 候補解の普遍性を検証する。余分がなく不足もない = 美"
  universal_property: "全ての候補解への一意的射を持つ解"
  precedent: "/boot v5.0 随伴深層統合 — 同パターンで成功"
  adjunction:
    notation: "F ⊣ G — 圏論を付与する (F) と 構造を発見する (G) の随伴対"
    unit: "η: Id → GF = Phase 3 (Kalon) — 付与→発見→元の問いと比較"
    counit: "ε: FG → Id = Phase 5 (Dokimasia) — 発見→付与→元に戻す"
cognitive_algebra:
  "+": 詳細分析（各フェーズで3倍の出力）
  "-": 要点分析（結論+理由1つのみ、5行以内）
  "*": メタ分析（分析の前提を問い直す）
sel_enforcement:
  "+":
    minimum_requirements:
      - "各 PHASE の出力が標準の3倍以上（文字数）"
      - "GoT (Graph of Thought) 分岐: 3つ以上の経路を探索"
      - "PHASE 3 (Kalon): 普遍性検証を実行"
      - "発想モード: Analogy/10x/Gap 等を最低1つ実行"
      - "最終出力: ファイル保存必須"
  "-":
    minimum_requirements:
      - "結論 + 理由1つのみ、5行以内"
---

# /noe: 最深層思考ワークフロー (Noēsis)

> **Hegemonikón**: O1 Noēsis（深い認識・直観）
> **関手**: F: Cat → Noe — 圏論の概念を思考プロセスに関手する
> **目的**: 直観的認識、前提破壊、0からの再構築。**Kalon（普遍的な美）** を持つ解を発見する。
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

## 処理フロー — 関手 F: Cat → Noe

> **設計思想**: /boot v5.0 が全 Phase を随伴関手 L の計算ステップとして再定義したように、
> /noe v6.0 は全 Phase を **圏論的操作** として定義する。
> 各 Phase の処理内容は変わらない。圏論的な **意味と言語** を与える。

1. **STEP 0**: SKILL.md を view_file で読み込む（必須・省略不可）
   // turbo

   ```
   view_file /home/makaron8426/oikos/hegemonikon/.agent/skills/ousia/o1-noesis/SKILL.md
   ```

2. **PHASE 0 — Prolegomena** (前限定): 図式 D の定義域 J を選ぶ
3. **PHASE 1 — Excavation** (対象の列挙): 圏の対象（前提）を炙り出す
4. **PHASE 2 — Genesis** (Cone の射を生成): 各仮説 = apex → 対象への射
5. **PHASE 3 — Kalon** (普遍性検証): Limit の頂点を発見する ← **新設**
6. **PHASE 4 — Synthesis** (射の合成と検証): 経路を辿り整合性を確認
7. **PHASE 5 — Dokimasia** (忠実性テスト): 関手 F が射を保存するか
8. **PHASE 6 — Theoria** (Yoneda 適用): Hom(-, 結論) で結論の完全性を検証
9. 最終出力: 構造化知見 → ファイル保存

---

## PHASE 2 発想モード (AI Zen 消化)

> **圏論的意味**: Phase 2 = Cone の射を生成する。各モードは射を異なる方向に伸ばす。

| モード | 説明 | プロンプト例 | 圏論 |
|:-------|:-----|:-------------|:-----|
| Analogy | 動物から連想 | 「この問題を解決する生物の戦略は？」 | 関手 F_bio |
| 10x | 10倍の目標 | 「目標を10倍にしたら？」 | 射の拡大 |
| Gap | 隙のあるアイデア | 「未成熟なたたき台を出す」 | 部分射 |
| Art | 芸術からの示唆 | 「この問題を表すアートは？」 | 関手 F_art |
| Random | ランダム組合せ | 「無関係な単語と組み合わせ」 | 余積 |
| Alien | 異質の取入れ | 「異なる分野のアプローチ」 | 外部関手 |

---

## PHASE 3: Kalon (普遍性検証) — Limit の頂点を発見する

> **圏論**: 圏 Cog における Limit = 全ての候補解への一意的射を持つ普遍的解。
> **Kalon**: τὸ καλόν = 美。余分がなく、不足もない。普遍的解はそれ自体が美しい。
> **FEP**: 普遍的解 = 自由エネルギーが最小な解（全候補を考慮した上での最適解）。

### 手順

| Step | 操作 | 圏論的意味 |
|:-----|:-----|:-----------|
| **K1: 図式化** | Phase 2 の候補解 (V1-V4 + Synthesis) を図式に配置 | D: J → Cog の構成 |
| **K2: 因子分解** | 各候補ペア: 「Aの解はBの特殊ケースか？」(LLM 判定) | f_i = h ∘ u の存在判定 |
| **K3: 普遍的候補** | 最も多くの候補を特殊ケースとして含む解を特定 | Limit の apex |
| **K4: 経済性** | 余分な仮定の少なさを Kalon スコア (0-1) で評価 | 普遍性の強さ |

### 出力形式

```
┌─[PHASE 3: Kalon (普遍性検証)]──────────────┐
│ 図式:                                       │
│   V1 ─→ Syn: 特殊化 (V1 は Syn の特殊ケース)│
│   V2 ─→ Syn: 特殊化                         │
│   V3 ─⊥─ Syn: 独立                          │
│   V4 ─→ Syn: 特殊化                         │
│                                              │
│ 普遍的候補: Synthesis                        │
│   射: 3/4, 一意性: MED                       │
│ Kalon: 0.75 — 仮定2つが余分                  │
│ 美: 「{解の美しさの1行記述}」                 │
└───────────────────────────────────────────────┘
```

### K2: 因子分解のプロンプト構造

> **精度優先**: テキスト包含率ではなく LLM に意味的な「特殊化の射」を判定させる。
> これは /noe の精神（コストより精度）に合致する。

```
以下の候補解について、包含関係（特殊化の射）を判定してください。

候補A: {V1の内容}
候補B: {V2の内容}

質問: A は B の特殊ケースか？ つまり B の方がより一般的で、
B に特定の条件を加えると A に退化するか？
→ YES/NO + 理由
```

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

## X-series 射の提案 (暗黙発動 L1)

> WF完了時、`/x` 暗黙発動プロトコルにより以下が自動提示される。
> 詳細: [x.md § 暗黙発動プロトコル](x.md)

```
🔀 射の提案 (trigonon: O/O1/Pure)
├─ Bridge >> S: /met /mek /sta /pra  (様態系 — 構造化)
├─ Bridge >> H: /pro /pis /ore /dox  (衝動系 — 直感検証)
└─ (完了)
```

---

## Hegemonikón Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| O1 Noēsis | /noe | v6.1 Ready |

> **制約リマインダ**: SKILL.md 読込 (STEP 0) → 全 Phase (0-6) を順序通り実行。PHASE 3 (Kalon) は省略不可。

---

*v5.1 — FBR 適用 (2026-02-07)*
*v6.0 — Kalon V3: 圏論深層統合。全 Phase を圏論的操作として定義。Phase 3 Kalon (普遍性検証) 新設 (2026-02-10)*
*v6.1 — 随伴対統合: η=Phase3, ε=Phase5 を発見・明記。Phase 6β (Theoria-G: 射出経路) 新設 (2026-02-10)*
*v6.2 — scaffold 派生追加 (PGH型: 骨格固定→創発→整流)。GoT lineage に #20 参照追記 (2026-02-10)*
