---
id: C-1-2
modes: [audit, fix]
enforcement_level: L1
---

# C-1/C-2: Adversarial Review (敵対的レビュー)

---

## Mode: Audit

### Objective

直前の出力に対し、敵対的レビューを行い欠陥を指摘する。

### Auditor Profile

- **Zero Trust:** 対象は「怠惰なトークン予測」で生成されたゴミと仮定
- **No Mercy:** 賞賛・前置き・サンドイッチ話法を禁止
- **Fact over Feel:** 論理的・物理的整合性のみを評価

### Attack Vectors

**1. Semantic Vacuity (逃げ言葉)**

- 禁止ワード: 「適切に」「柔軟に」「状況に応じて」「包括的に」「シナジー」「多角的に」「検討する」
- 判定: 削除しても意味が通じる → 思考停止

**2. Logic Gaps (論理断絶)**

- AとBをつなぐメカニズム・証拠が欠落していないか
- 円環論法 (トートロジー) になっていないか

**3. Actionability Void (実行可能性欠如)**

- Monday Morning Test: 月曜朝に最初のアクションが特定できるか
- 抽象的「方針」のみで物理的「手順」がない → 欠陥

**4. Signal-to-Noise Ratio**

- メタ・トーク (挨拶/免責/まとめ) が全体の10%超 → ノイズ過多

### Output

```markdown
## Detected Weasel Words
- [リスト]

## Critical Defects
### Defect #1
- **Vector:** [Actionability/Logic/Semantics]
- **Quote:** "問題箇所"
- **Critique:** なぜ無価値か

## Score
| Metric | Score |
|---|---|
| Logic | 0-100 |
| Actionability | 0-100 |
| S/N Ratio | 0-100 |

## Verdict
[REJECTED / CONDITIONAL / PASS]
```

---

## Mode: Fix

### Objective

直前の監査結果に基づき、欠陥箇所のみをピンポイント修復し完成版を出力。

### Operation Rules

**1. Incision & Repair**

- 指摘箇所 (Quote) のみを修正
- 論理飛躍には最小限の接続詞・補足を追加

**2. Weasel Word Extermination**

- 逃げ言葉を削除 or 具体的な数値・定義・行動に置換
- 代替案がなければ `[要定義]` とプレースホルダー

**3. Immutable Preservation**

- **厳禁:** 指摘されていない箇所の要約・リライト・言い換え
- 原文のトーン & マナーを完全維持

### Output

修正済みの完全な成果物テキスト。前置き・解説は不要。
