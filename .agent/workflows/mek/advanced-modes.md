---
summary: 高度モード。reverse (逆生成), constitutional (原則優先度), yaml (ハイブリッド), multi (並列専門家)。
hegemonikon: S2 Mekhanē
parent: ../mek.md
origin: 2026-02-01 Perplexity Task 4
---

# 高度モード (Advanced Modes)

> S2 Mekhanē — メタ生成と多視点統合のための4つの高度手法。

## Constraints

- 出力はテーブル形式で構造化する
- 各モードの理論的背景を明記する
- 信頼度・トレードオフを必ず含める

---

## reverse — 逆プロンプト生成

**CCL**: `/mek.reverse` = `/mek*{direction=backward}`
**目的**: 高品質な出力例から、それを再現するプロンプトを逆生成する
**発動**: `/mek reverse` または「この出力を再現」「プロンプト逆生成」

**理論**: 良い出力があるがプロンプトがわからない。「出力→入力」の逆方向推論。SAGE Mode のポスト処理として有効。

### Process

1. 高品質な出力例を入力として受け取る
2. 構造分析: フォーマット/論理構造/トーン・スタイルを特定
3. プロンプト要素推定: FORMAT, CONTEXT, INTENT を抽出
4. プロンプトを生成
5. 検証: 生成プロンプトで同等出力が得られるか確認

### Output Format

**[S2 Mekhanē: Reverse]**

| フィールド | 内容 |
|:-----------|:-----|
| 入力 | {出力例の概要} |
| FORMAT | {フォーマット特性} |
| TONE | {トーン・スタイル} |
| STRUCTURE | {論理構造} |
| 生成プロンプト | {推定されたプロンプト} |
| 信頼度 | {HIGH/MEDIUM/LOW} |
| 検証方法 | {再実行して比較} |

---

## constitutional — 原則優先度付き生成

**CCL**: `/mek.constitutional` = `/mek+{governance=principles}`
**目的**: 原則に優先度を付け、優先原則に反しない生成を保証する
**発動**: `/mek constitution` または「原則に従って」「Constitutional」

**理論**: 複数原則衝突時の解決。優先度明示による一貫性担保。Internal Council に PRINCIPLE 層を追加。

### Process

1. 原則定義: P1 (最優先), P2 (重要), P3 (望ましい)
2. 草案生成: 通常の生成プロセスを実行
3. 原則チェック: P1違反 → 全面書直し、P2違反 → 部分修正、P3違反 → 可能なら調整
4. 最終出力 + 「P1-P3 を満たす」証明を付与

### Output Format

**[S2 Mekhanē: Constitutional]**

| 優先度 | 原則 | 準拠状態 | 理由 |
|:-------|:-----|:---------|:-----|
| P1 (必須) | {原則1} | {準拠/違反} | {理由} |
| P2 (重要) | {原則2} | {準拠/違反} | {理由} |
| P3 (望ましい) | {原則3} | {準拠/部分} | {トレードオフ} |

| フィールド | 内容 |
|:-----------|:-----|
| 生成物 | {原則に準拠した成果物} |

---

## yaml — YAML+MD ハイブリッド出力

**CCL**: `/mek.yaml` = `/mek+{format=yaml_hybrid}`
**目的**: 構造化データは YAML、説明文は Markdown のハイブリッド出力
**発動**: `/mek yaml` または「YAML形式」「構造化出力」

**理論**: XMLより人間可読性が高い。LLMとの親和性が高いフォーマット。構造データと説明文の分離。

### Output Format

```yaml
---
title: "{タイトル}"
version: "1.0"
metadata:
  scale: "Meso"
  archetype: "Precision"
  confidence: "HIGH"
---
```

上記 YAML ヘッダーに続けて Markdown 本文で概要・構造データ・結論を記述する。

---

## multi — 並列専門家対話

**CCL**: `/mek.multi` = `/mek+{actors=parallel_experts}`
**目的**: 複数専門家を並列実行し、統合見解を生成する
**発動**: `/mek multi` または「複数専門家」「並列エキスパート」

**理論**: 単一視点の限界を超える。CONFLICT フェーズの強化版。`/dia.deliberative` との補完関係。

### Process

1. 課題を定義し、3名の専門家を選定
2. 各専門家が独立に見解を出力
3. 衝突検出: 専門家間の矛盾点を特定
4. 統合見解を生成し、トレードオフを明示

### Output Format

**[S2 Mekhanē: Multi-expert]**

| Expert | 専門分野 | 見解 |
|:-------|:---------|:-----|
| A | {分野1} | {見解A} |
| B | {分野2} | {見解B} |
| C | {分野3} | {見解C} |

| 衝突 | 内容 |
|:-----|:-----|
| A vs B | {衝突内容} |
| B vs C | {衝突内容} |

| フィールド | 内容 |
|:-----------|:-----|
| 統合見解 | {調停された最終見解} |
| トレードオフ | {何を優先し、何を犠牲にしたか} |

---

## Reminder

- 出力はテーブル形式。信頼度・トレードオフを必ず明示する
- 理論的背景を省略しない

*Advanced Modes v2.0 — Functional Beauty Redesign*
