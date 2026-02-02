# 調査依頼書（深掘り版）

テーマ: **Jules に Prompt-Lang DSL を使わせる方法**

---

## 0. あなた（調査者）への依頼（最重要）

私は **Prompt-Lang** という独自のプロンプト定義言語（DSL）を開発し、MVP が完成した。
この言語を **Google Jules（GitHub Copilot Workspace の Gemini Code Assist 版）** に理解させ、**Prompt-Lang 形式でプロンプトを生成させたい**。

以下について、**一般論で終わらせず**、2024-2026時点の最新仕様・挙動・制約を**一次情報と再現性のある検証情報**で裏付けてほしい:

1. **Jules のカスタマイズ可能性**: システムプロンプト/ルール/指示の注入方法
2. **DSL 学習の最適な方法**: Few-shot? GEMINI.md 経由? 専用リポジトリ?
3. **実装パターン**: 既存の「言語をLLMに教える」事例（例: SQL生成、GraphQL生成）

結論は「どっちが上」ではなく、**Jules に Prompt-Lang を使わせるための具体的な実装手順**まで落とし込んで提示してほしい。

---

## 1. 調査対象の定義

### 1-1. 製品名・モード名の確認

- **Jules**: Google の AI コーディングエージェント（Gemini Code Assist の一部）
- **Prompt-Lang**: 独自開発の DSL（`#prompt`, `@role`, `@goal`, `@constraints`, `@context`, `@if/@else`, `@rubric` などのディレクティブを持つ）

### 1-2. Prompt-Lang の仕様

```
#prompt example
@role:
  シニアエンジニア
@goal:
  コードレビューを行う
@context:
  - file:"path/to/file.py" [priority=HIGH]
@constraints:
  - 建設的なフィードバック
@if env == "prod":
  @constraints:
    - 破壊的変更は禁止
@endif
```

---

## 2. 調査すべき論点

### A. Jules のカスタマイズ方法

**A1. 公式ガイドライン**
- Jules にカスタムルールや DSL を教える公式の方法はあるか？
- `.gemini/` ディレクトリ、`GEMINI.md`、`.jules/` などの設定ファイルは利用可能か？

**A2. システムプロンプトへのアクセス**
- Jules のシステムプロンプトをカスタマイズできるか？
- 「常にこの形式で出力せよ」という指示をどこに書くか？

### B. DSL 学習パターン

**B1. Few-shot プロンプティング**
- 例示を通じて Prompt-Lang 形式を学習させる方法
- 必要な例示数、配置場所

**B2. リポジトリベースの学習**
- 専用リポジトリに `.prompt` ファイルを配置し、Jules に参照させる方法
- `docs/` に仕様書を置くことの効果

**B3. 明示的なルール注入**
- `GEMINI.md` や `AGENTS.md` に Prompt-Lang 仕様を記載する方法

### C. 類似事例

**C1. SQL/GraphQL 生成**
- LLM に特定のクエリ言語を出力させる既存手法

**C2. DSL in Production**
- 企業が LLM に独自 DSL を教えた事例（もしあれば）

---

## 3. 成果物

1. **結論サマリー**（10行以内）
2. **Jules カスタマイズ方法一覧**
3. **Prompt-Lang 導入手順**（ステップバイステップ）
4. **根拠リンク**（必須）

---

## 4. 調査ルール

- **新情報優先**: 2024-2026 の情報を優先
- **事実/推測分離**: 必ず明確に分離
- **根拠必須**: 公式ドキュメントまたは検証記事を引用

---

## 5. 与件

- **目的**: Jules に Prompt-Lang 形式でプロンプトを生成させる
- **前提条件**: Prompt-Lang MVP 完成済み、仕様書あり
- **リポジトリ**: https://github.com/laihuip001/hegemonikon
- **優先する評価軸**: 実装可能性 > 信頼性 > 簡便さ

---

## 6. パプ君（Perplexity）最終レポート

### 主要発見

**結論**: Jules での Prompt-Lang 単独統合は「技術的に困難」だが、**Claude + MCP ラッパー経由** で完全実装可能。信頼度 **95%**。

### 調査結果

| 層 | 調査対象 | 発見 |
|:---|:---|:---|
| A層 | GitHub Issues: "Jules + DSL" | ❌ 0件 |
| B層 | `.gemini/` の実装パターン | ✅ 508 stars テンプレート検出 |
| C層 | Claude/Cursor での DSL 事例 | ✅✅ 20+ 実装例 |

### 最適アーキテクチャ

```
Antigravity IDE → Claude (Agent Mode) → MCP Communication → Prompt-Lang MCP Server
```

### 推奨戦略

1. **即座に実施**: `.mcp.json` 設定
2. **Week 1-2**: MCP サーバー実装 (parse, validate, generate)
3. **Week 3**: E2E テスト
4. **Week 4**: ドキュメント・公開

### 競合比較

| 観点 | Jules 単独 | Claude + MCP |
|:---|:---:|:---:|
| 公開ドキュメント | ❌ | ✅ 充実 |
| GitHub 実装例 | ❌ 0件 | ✅ 20+ |
| スケーラビリティ | ⚠️ | ✅ |

**結論**: Claude + MCP が圧倒的に有利。
