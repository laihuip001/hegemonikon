# 調査依頼書（深掘り版）

テーマ: **LLM向け構造化プロンプト生成 Skill の最新プラクティス**

---

## 0. あなた（調査者）への依頼（最重要）

私は Antigravity IDE（Claude駆動）用の **Prompt-Lang コード生成 Skill** を構築しようとしている。

Prompt-Lang とは、独自に設計した構造化プロンプト記述言語であり、以下のディレクティブを持つ:
- `@role`, `@goal`, `@constraints`, `@format`, `@examples`, `@tools`, `@resources`（v1）
- `@rubric`, `@if/@else`, `@activation`, `@context`, `@extends`, `@mixin`（v2）

以下について、**一般論で終わらせず**、2024-2026時点の最新仕様・挙動・制約を**一次情報と再現性のある検証情報**で裏付けてほしい:

1. **「プロンプト生成プロンプト」のベストプラクティス**: Meta-prompting、Prompt Chaining、Self-Ask、APE（Automatic Prompt Engineer）など、プロンプトを生成するプロンプトの最新手法
2. **構造化プロンプト言語の類似実装**: DSPy、LMQL、Guidance、PDL（IBM）、TypeChat などの設計思想と比較
3. **Claude Skill としての実装パターン**: Antigravity / Claude Projects / MCP における Skill 設計のベストプラクティス

結論は「どれが最良」ではなく、**Prompt-Lang Skill 設計に活かせる具体的知見**と**避けるべきアンチパターン**まで落とし込んで提示してほしい。

---

## 1. 調査対象の定義（用語の揺れに対応）

### 1-1. 製品名・手法名の確認

まず以下を確定してください（曖昧なまま比較しないこと）:

- **Meta-prompting**: Zhou et al. (2022) APE と、最近の "Large Language Models as Optimizers" の区別
- **DSPy**: v2.0 以降の最新 API と設計思想
- **LMQL**: 最新バージョンでの制約型プロンプティング機能
- **PDL (Prompt Declaration Language)**: IBM Research の 2024 発表分
- **Guidance (MS)**: 現在のメンテナンス状況と後継

### 1-2. 比較対象

| 分類 | 対象 |
|:---|:---|
| **Meta-prompting手法** | APE, OPRO, PromptBreeder, EvoPrompt |
| **構造化言語** | DSPy, LMQL, Guidance, PDL, TypeChat |
| **IDE/Skill設計** | Claude Projects, Anthropic MCP, Cursor Rules |

---

## 2. 調査すべき論点（抜け漏れ禁止）

以下を必ず網羅し、断定できない場合は「不確実」と明示し、追加検証手順を示してください。

### A. Meta-prompting 手法の比較

**A1. 学術文献ベースの比較**

| 手法 | 論文 | 核心アイデア | Prompt-Lang への適用可能性 |
|:---|:---|:---|:---|
| APE | Zhou 2022 | | |
| OPRO | Yang 2023 | | |
| PromptBreeder | Fernando 2024 | | |
| EvoPrompt | Guo 2024 | | |

**A2. 実務での採用事例**
- 各手法を本番で使用した事例、成功/失敗報告
- 必要なインフラ（反復回数、評価データセット、計算コスト）

### B. 構造化プロンプト言語の比較

**B1. 設計思想の違い**

| 言語 | 制御の中心 | 型安全性 | 実行モデル |
|:---|:---|:---|:---|
| DSPy | | | |
| LMQL | | | |
| Guidance | | | |
| PDL | | | |
| TypeChat | | | |
| **Prompt-Lang** | ディレクティブ | なし（YAML風） | 静的コンパイル |

**B2. 機能マッピング**

以下のPrompt-Lang機能に対応する他言語の機能を整理:
- `@if/@else` → 条件分岐
- `@context` → リソース参照
- `@rubric` → 自己評価
- `@extends/@mixin` → 再利用

### C. Claude Skill 設計のベストプラクティス

**C1. 公式ドキュメント・ガイドライン**
- Anthropic 公式の Skill 設計ガイド（あれば）
- Claude Projects のベストプラクティス
- MCP サーバ設計原則

**C2. コミュニティ知見**
- 評価の高い Skill 実装例（GitHub、ブログ）
- 失敗事例・アンチパターン

### D. プロンプト生成における品質指標

**D1. 評価メトリクス**
- 生成されたプロンプトの品質をどう測定するか
- Human eval vs Automated eval（LLM-as-judge）

**D2. 反復改善戦略**
- 一発生成 vs 反復改善
- フィードバックループの設計

---

## 3. 成果物（この構成で必ず提出）

1. **結論サマリー**（10行以内）: Prompt-Lang Skill 設計への3つの核心推奨事項
2. **Meta-prompting 比較表**: 手法 × 適用コスト × Prompt-Lang親和性
3. **構造化言語 比較表**: 言語 × 設計思想 × 学べる点
4. **Skill 設計パターン集**: 推奨パターン3-5個 + アンチパターン3-5個
5. **具体的実装提案**: Prompt-Lang Skill の骨格設計案
6. **根拠リンク**（必須）:
   - 論文リンク（arXiv, ACL Anthology 等）
   - 公式ドキュメント
   - 評価の高い実装例

---

## 4. 調査ルール（品質担保）

- **新情報優先**: 2024-2026の情報を優先（古い手法でも最新評価を参照）
- **事実/推測分離**: 必ず明確に分離
- **学術 vs 実務**: 論文の結果と実務での採用状況を区別
- **根拠必須**: 「一般に〜と言われる」で終わらず、根拠・再現例・反例を提示
- **決断可能**: Prompt-Lang Skill 設計に直結する actionable な結論

---

## 5. 追加要件（任意だが望ましい）

- **評価テンプレ**: Prompt-Lang 生成物の品質を測る評価セット（5問程度）
- **失敗パターン集**: プロンプト生成系 Skill でありがちなミス
- **参考実装リンク**: 優れた Skill 実装の GitHub リポジトリ

---

## 6. 与件（ユーザー観測データ/背景/制約/目的）

### 目的
- Antigravity IDE 内で Prompt-Lang コードを高品質に生成する Skill を構築
- メタプロンプト技術を活用し、「プロンプトを書くプロンプト」の品質を最大化

### 前提条件
- 環境: Antigravity IDE（Claude Sonnet 4 駆動）
- 既存資産: `meta-prompt-generator` Skill（324行、アーキタイプ駆動設計）
- Prompt-Lang: v2.0 実装済み（`@context` `@if/@else` `@rubric` `@activation`）

### 検討中の仮説
1. **アーキタイプ駆動**: 既存 Skill の設計を継承すべき
2. **テンプレート + 可変部**: Prompt-Lang の定型構造をテンプレート化し、可変部のみ生成
3. **自己評価ループ**: `@rubric` を使って生成物を自己評価 → 改善

### 優先する評価軸
1. **正確性**: 構文エラーのない Prompt-Lang コード生成
2. **実用性**: 実際に機能する高品質プロンプト出力
3. **網羅性**: 適切なディレクティブの選択・組み合わせ
