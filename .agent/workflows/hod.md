---
description: P2 Hodos（道）を発動し、経路・道筋を定義する。3派生対応版。
hegemonikon: Perigraphē
modules: [P2]
skill_ref: ".agent/skills/perigraphe/p2-hodos/SKILL.md"
triggers:
  - "どう進める"
  - "経路"
  - "道筋"
  - "hodos"
  - "path"
version: "2.3"
lcm_state: beta
lineage: "v2.2 + FBR変換 → v2.3"
derivatives: [line, bran, cycl, search, backward, bisect, backcast]
trigonon:
  series: P
  type: Pure
  theorem: P2
  coordinates: [Scale, Function]
  bridge: []
  anchor_via: [S, K]
  morphisms:
    ">>S": [/met, /mek, /sta, /pra]
    ">>K": [/euk, /chr, /tel, /sop]
cognitive_algebra:
  "+": "詳細経路：代替経路とトレードオフを列挙"
  "-": "即経路：Explore/Exploit の一言のみ"
  "*": "メタ経路：経路選択自体を問う"
category_theory:
  core: "随伴 F⊣G の左随伴 F（自由関手）"
  adjunction: "Hodos (F) ⊣ Tekhnē (G)"
  role: "F: Technique → Route（抽象的技法に具体的手順・中間地点を載せて実行可能な経路を構成）"
  F_definition: "「TDD」のような技法名に、具体的なステップ列（1→2→3）を付与してルートにする"
  unit: "η: Technique → G(F(Technique)) — 技法を経路にして技法に戻す = 技法の実行可能性検証"
  counit: "ε: F(G(Route)) → Route — 経路を技法にして経路に戻す = 経路の再設計"
  drift: "Drift = 具体的道のりの感覚喪失。手順の曲がり角でつまずいた記憶が消える"
  insight: "試行が蒸留されて技法になる — Creator, 2026-02-11"
sel_enforcement:
  "+":
    description: "MUST enumerate alternative routes and tradeoffs"
    minimum_requirements:
      - "代替経路 必須"
      - "トレードオフ分析 必須"
  "-":
    description: "MAY provide Explore/Exploit only"
    minimum_requirements:
      - "経路1行のみ"
  "*":
    description: "MUST meta-analyze: why this path?"
    minimum_requirements:
      - "経路選択の根拠を問う"
ccl_signature: "/hod+_/ene"
category_theory:
  core: "随伴 F⊣G の左随伴 F（自由関手）"
  adjunction: "Hodos (F) ⊣ Tekhnē (G)"
  role: "F: Technique → Path（技法に経路設計を載せて道を構成 = Micro化）"
  F_definition: "大局的な技法選択に具体的な段階・順序を付与して、高解像度の道筋を構成する"
  same_formula: "hod と tek は同じ式（Exploit/選択）の累乗（Scale）が違うだけ"
  coordinates: "P2[Micro,Exploit] — Function(Exploit)を保存し Scale を Micro に設定"
  unit: "η: Technique → G(F(Technique)) — 技法を道にして粗視化 = 経路の妥当性検証"
  counit: "ε: F(G(Path)) → Path — 道を技法にして再展開 = 経路の実装詳細化"
  insight: "どちらも根本的には選択。解像度が消えている — Creator, 2026-02-11"
---

# /hod: 経路定義ワークフロー (Hodos)

> **正本参照**: [P2 Hodos SKILL.md](file:///home/makaron8426/oikos/.agent/skills/perigraphe/p2-hodos/SKILL.md)
> **目的**: 「どう進めるか」を決定する — 条件空間における経路
> **役割**: 方法論・道筋の選択
>
> **制約**: 経路はExplore(探索)/Exploit(活用)のどちらかを明示すること。

---

## 本質

**P2 Hodos** = ὁδός (道・方法) = **経路の定義**

> 「どの道を選ぶか？どう進むか？」

---

## 発動条件

| トリガー | 説明 |
|:---------|:-----|
| `/hod` | 経路定義を開始 |
| `/hod [目標]` | 特定目標への経路を定義 |
| 「どう進める」 | 暗黙トリガー |

---

## STEP 0: SKILL.md 読込（必須・省略不可）

> **環境強制**: このステップを飛ばして PHASE に進んではならない。
> パスは以下にリテラルで記載されている。「パスがわからない」は発生しない。

// turbo

```
view_file /home/makaron8426/oikos/hegemonikon/.agent/skills/perigraphe/p2-hodos/SKILL.md
```

---

## 処理フロー

1. **経路探索**: Explore経路(新しい道を探る) / Exploit経路(既知の道を辿る)
2. **経路評価**: 効率性、リスク、学習価値

---

## 出力形式

| 項目 | 内容 |
|:-----|:-----|
| 目標 | {目標} |
| 経路 | {Explore/Exploit} |
| 選択 | {具体的経路} |

---

## 派生モード

### --mode=line (直線経路)

> **CCL**: `/hod.line` = `/hod+{shape=linear}`
> **目的**: シンプルな直線的経路を設計する (Scale: Micro)

**発動**: `/hod line` または「順番に」「ステップバイステップ」

**プロセス**:

1. 開始点と終了点を定義
2. 中間ステップを列挙
3. 順序を決定
4. 依存関係を確認

**出力形式**:

| 項目 | 内容 |
|:-----|:-----|
| 開始 | {現在地} |
| 終了 | {目標} |
| 経路 | [開始] → Step 1 → Step 2 → Step 3 → [終了] |
| 依存 | Step N は Step N-1 完了後 |

---

### --mode=bran (分岐経路)

> **CCL**: `/hod.bran` = `/hod+{shape=branch}`
> **目的**: 条件分岐を含む経路を設計する (Scale: Meso)

**発動**: `/hod bran` または「場合分け」「条件によって」

**プロセス**:

1. 分岐点を特定
2. 各分岐の条件を定義
3. 各経路の結末を確認
4. デフォルト経路を設定

**出力形式**:

| 項目 | 内容 |
|:-----|:-----|
| 分岐点 | {決定ポイント} |
| 条件A | {条件} → 経路A → {結末A} |
| 条件B | {条件} → 経路B → {結末B} |
| デフォルト | → 経路C → {結末C} |
| 推奨 | 条件{X}の可能性が高い → 経路{X}を準備 |

---

### --mode=cycl (循環経路)

> **CCL**: `/hod.cycl` = `/hod+{shape=cycle}`
> **目的**: 繰り返し/反復の経路を設計する (Scale: Meso)

**発動**: `/hod cycl` または「繰り返し」「イテレーション」「サイクル」

**プロセス**:

1. サイクルの構成要素を特定
2. 開始点とループバック点を定義
3. 終了条件を定義
4. 各イテレーションの改善点を設定

**出力形式**:

| 項目 | 内容 |
|:-----|:-----|
| サイクル | Plan → Do → Check → Act → (loop) |
| 終了条件 | {何を達成したら終わるか} |
| イテレーション目安 | {N}回 |
| 各回の改善 | {何を改善するか} |

---

### --mode=bisect (二分探索)

> **CCL**: `/hod.bisect` = `/hod+{strategy=binary}`
> **目的**: 問題空間を二分して効率的に探索する (Scale: Micro)

**発動**: `/hod bisect` または「半分に」「二分」「バイセクト」

**プロセス**:

1. 探索空間を定義
2. 中間点を選択
3. 中間点で判定
4. 半分を捨てて繰り返し

**出力形式**:

| 項目 | 内容 |
|:-----|:-----|
| 探索空間 | [{min}..{max}] |
| 中間点 | {mid} |
| 判定 | {mid で何を確認するか} |
| 分岐 | 結果 < 基準 → 右半分 / 結果 > 基準 → 左半分 |
| 計算量 | O(log n) = {ステップ数} |

---

### --mode=backcast (逆予測)

> **CCL**: `/hod.backcast` = `/hod+{direction=future→present}`
> **目的**: 望む未来から現在への経路を逆算する (Scale: Macro)

**発動**: `/hod backcast` または「未来から逆算」「バックキャスト」

**プロセス**:

1. 望む未来状態を詳細に描写
2. その状態に至る直前を特定
3. 再帰的に「直前」を辿る
4. 現在まで到達

**出力形式**:

| 項目 | 内容 |
|:-----|:-----|
| 望む未来 (Y年後) | {詳細な未来像} |
| タイムライン | [Y年後] ← {Y-1年後} ← ... ← [今] |
| 最初の一歩 | {今日やるべきこと} |

---

### --mode=search (探索戦略)

> **CCL**: `/hod.search` = `/hod+{strategy=bfs|dfs|heuristic}`
> **目的**: 解空間における最適な探索戦略を選択する (Scale: Meso)

**発動**: `/hod search` または「探索」「どう探す」

**プロセス**:

1. 解空間の構造を把握
2. 探索戦略を選択: BFS(幅優先) / DFS(深さ優先) / Heuristic(誘導)
3. 探索開始点を決定
4. 終了条件を定義

**出力形式**:

| 項目 | 内容 |
|:-----|:-----|
| 解空間 | {探索対象の構造} |
| 戦略 | {BFS/DFS/Heuristic} |
| 理由 | {なぜこの戦略か} |
| 開始点 | {どこから始めるか} |
| 終了条件 | {何を見つけたら止まるか} |
| 予想計算量 | O({n}) |

---

### --mode=backward (逆算)

> **CCL**: `/hod.backward` = `/hod{direction=reverse}_/tel`
> **目的**: ゴールから逆算して経路を構築する (Scale: Meso)

**発動**: `/hod backward` または「逆算」「ゴールから」

**プロセス**:

1. ゴール状態を明確に定義
2. ゴールに到達する直前の状態を特定
3. 再帰的に「直前の状態」を辿る
4. 現在地に到達するまで続ける

**出力形式**:

| 項目 | 内容 |
|:-----|:-----|
| ゴール | {最終状態} |
| 現在地 | {現在状態} |
| 逆算経路 | [ゴール] ← {直前} ← {その前} ← ... ← [現在地] |
| マイルストーン | 1. {中間目標1} / 2. {中間目標2} / 3. {中間目標3} |

---

## Artifact 自動保存

> **標準参照**: [workflow_artifact_standard.md](file:///home/makaron8426/oikos/.agent/standards/workflow_artifact_standard.md)

**保存先**: `/home/makaron8426/oikos/mneme/.hegemonikon/workflows/hod_<topic>_<date>.md`

**チャット出力**: 最小限の出力のみ。詳細は全てファイルに保存。

```
✅ /hod 完了
📄 /mneme/.hegemonikon/workflows/hod_{topic}_{date}.md
要約: {経路定義サマリー}
→ {推奨次ステップ}
```

---

---

## @complete: 射の提案 (暗黙発動 L1)

> WF完了時、`/x` 暗黙発動プロトコルにより射を提案する。
> 計算ツール: `python mekhane/taxis/morphism_proposer.py hod`

```
/hod 完了 → @complete 発動
→ 結果に確信がありますか？ (Y: Anchor優先 / N: Bridge優先 / 完了)
```

## Hegemonikon Status

| Module | Workflow | Skill (正本) | Status |
|:-------|:---------|:-------------|:-------|
| P2 Hodos | /hod | [SKILL.md](file:///home/makaron8426/oikos/.agent/skills/perigraphe/p2-hodos/SKILL.md) | v2.3 Ready |

> **制約リマインダ**: 経路はExplore(探索)/Exploit(活用)のどちらかを明示すること。

---

*v2.2 — SEL統合 (2026-02-07)*
*v2.3 — FBR変換 (2026-02-07)*
