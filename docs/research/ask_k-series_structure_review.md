# 調査依頼書（深掘り版）

テーマ: **AI/LLM用 SKILL.md ファイルの最適構造設計**

---

## 0. あなた（調査者）への依頼（最重要）

私は LLM エージェント (Claude) が参照する「Skill」ドキュメント（SKILL.md）の構造を最適化しようとしている。

現在、12個の「K-series（文脈定理）」SKILL.md を作成したが、**粒度・情報密度・セクション順序が最適か不明**である。

以下について、**LLMコグニティブエンジニアリングとプロンプト設計の最新知見**を踏まえて検証してほしい:

1. **構造の妥当性**: 各セクションの役割、順序、粒度は適切か
2. **情報密度**: LLMが参照する際に過不足ないか（冗長 vs 不足）
3. **美しさ**: 認知負荷を下げる構造設計のベストプラクティス

結論は「一般論」ではなく、**具体的な改善提案**として提示してほしい。

---

## 1. 調査対象の定義

### 1-1. 現在の SKILL.md 構造（サンプル: K1）

```markdown
---
name: "K1 Tempo→Stratum"
description: |
  文脈定理 K1: 時間制約が処理レベルを決定する。
  Use when: ...
  Use when NOT: ...
  Triggers: ...
  Keywords: ...
---

# Κ1: Tempo → Stratum

> **問い**: ...
> **選択公理**: ...
> **役割**: ...

---

## Core Function
## Matrix
## Trigger
## Processing Logic
## 適用ルール
## Edge Cases
## Test Cases
## 1:3 ピラミッド（代表例）
## Integration
## Configuration
```

### 1-2. 文脈

- **用途**: LLMエージェント (Claude/Antigravity) がセッション中に参照する
- **読者**: LLM（人間も読むが主要読者はLLM）
- **YAML frontmatter**: Antigravity IDE の Skill 検索で使用
- **Markdown本文**: LLM がコンテキストとして読み込む

---

## 2. 調査すべき論点（抜け漏れ禁止）

### A. LLM向けドキュメント設計の最新知見

**A1. 構造化プロンプト/ドキュメントの効果**
- YAML frontmatter vs Markdown 本文の使い分け
- セクション順序が LLM の理解に与える影響
- 情報密度と認知負荷のバランス

**A2. 実務タスクにおける効果**
- LLM が参照する際に「見つけやすい」構造
- 行動可能な情報（Trigger, Rules）の最適配置
- 例示（1:3 ピラミッド）の効果

### B. セクション順序の最適化

以下の2つの観点で比較検証:

1. **認知的流れ**: 「なぜ」→「何」→「どう」→「例外」→「例」
2. **実用的流れ**: 「いつ使う」→「何をする」→「どう判断」→「失敗パターン」

**現在の順序**:
1. YAML frontmatter (name, description, Use when, Triggers, Keywords)
2. Header (問い, 選択公理, 役割)
3. Core Function
4. Matrix
5. Trigger
6. Processing Logic
7. 適用ルール
8. Edge Cases
9. Test Cases
10. 1:3 ピラミッド
11. Integration
12. Configuration

**質問**: この順序は最適か？順序変更で効果が上がるか？

### C. 情報粒度の評価

| セクション | 現在の粒度 | 質問 |
|------------|-----------|------|
| YAML frontmatter | 詳細 | 適切か？LLM検索に必要十分か？ |
| Matrix | 2x2 | 4セル全てに詳細が必要か？ |
| Edge Cases | 3行程度 | もっと網羅すべきか？ |
| Test Cases | 5例 | 数は適切か？ |
| 1:3 ピラミッド | 3例 | 代表例として十分か？ |

### D. 比較対象

以下の既存フレームワークと比較:

1. **Anthropic の System Prompt 設計ガイド**
2. **OpenAI の Function Calling スキーマ**
3. **LangChain/LangGraph の Tool 定義形式**
4. **Google の Prompt Engineering ガイド**

### E. 美学的観点

- **視覚的バランス**: テーブル vs リスト vs コードブロック
- **名前の一貫性**: 英語 vs 日本語 vs ギリシャ語
- **空白の使い方**: セクション間の余白

---

## 3. 成果物（この構成で必ず提出）

1. **結論サマリー**（10行以内）: 現在の構造の評価と主要改善点
2. **セクション順序比較表**: 現在 vs 推奨 vs 理由
3. **情報粒度評価**: 各セクションの over/under 評価
4. **推奨テンプレート**: 改善後の SKILL.md 構造
5. **根拠リンク**: 参照した研究/ガイド/実践例

---

## 4. 調査ルール（品質担保）

- **新情報優先**: 2024-2026の LLM プロンプト設計知見を優先
- **事実/推測分離**: 研究に基づく知見 vs 経験則を明確に分離
- **具体的提案**: 「〜すべき」ではなく「〜をこう変更」の形で
- **再現可能**: 提案の効果を検証する方法も提示

---

## 5. 与件（ユーザー観測データ）

### 現在の SKILL.md サンプル（K1）

（上記に記載済み）

### 参考: T-series の構造（~250行、充実版）

T-series は以下のセクションを持つ:
- Core Function
- Precondition
- Input / Output
- Trigger
- Processing Logic
- Classification Criteria
- Entity Detection Patterns
- Calculation Formulas
- Edge Cases
- Test Cases
- Failure Modes
- Integration
- Configuration
- Limitations

**質問**: K-series も同等の粒度が必要か？それとも用途が異なるため簡素で良いか？

---

## 6. 優先する評価軸

1. **LLM の行動効率**: 参照して即座に行動できるか
2. **認知負荷の最小化**: 不要な情報で混乱しないか
3. **美しさ**: 構造的整合性、命名の一貫性
4. **保守性**: 将来の拡張・修正が容易か
