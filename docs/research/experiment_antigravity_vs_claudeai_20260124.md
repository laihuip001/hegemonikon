# 実験レポート: Antigravity Claude vs claude.ai

**日時**: 2026-01-24 22:40
**目的**: プロンプト生成能力の比較

---

## 課題

「コードレビュー用のシステムプロンプトを Prompt-Lang v2 形式で作成」

---

## 結果

| 環境 | 出力特性 | 評価 |
|:---|:---|:---|
| Antigravity Claude（Skillなし） | 簡潔・実装寄り | △ |
| Antigravity Claude（meta-prompt-generator Skill適用） | 体系的・工学的・Precision特化 | ✅ |
| claude.ai | 汎用・教育的・人間向け | ✅ |
| **Web Jules (Gemini)** | 仕様準拠・簡潔・実用的 | ✅ |

---

## 主要な違い

| 観点 | claude.ai | Antigravity + Skill | Web Jules |
|:---|:---|:---|:---|
| 設計思想 | バランス型 | Precision特化 | 仕様準拠型 |
| 出力形式 | Markdown（人間向け） | JSON（機械処理向け） | Markdown（人間向け） |
| 確信度 | なし | 0.0-1.0定量化 | なし |
| CVSSスコア | なし | 完全対応 | 言及のみ |
| Fallback | なし | 明示定義 | なし |
| @context 活用 | テンプレート変数 | 実ファイル | **file, ki, mcp 3種全て** |

---

## 重要な発見

### 1. Web Jules は Prompt-Lang を「学習」できた

- 仕様を渡すだけで DSL 形式を正確に生成
- パース可能な `.prompt` ファイルを出力
- 軽微な修正（プロンプト名の形式）のみで完全準拠

### 2. Web Jules vs Antigravity Jules

| 特性 | Web Jules | Antigravity Jules |
|:---|:---|:---|
| 実行速度 | 遅い（45分+） | 速い（42秒） |
| **品質** | ✅ 高品質 | ✅ 高品質 |
| UI応答性 | 500-1000ms | <100ms |
| 並列能力 | 単一タスク | 8エージェント |

**結論**: Web Jules の制限は「速度」であって「品質」ではない。

---

## 結論

**Skill を使えば Antigravity 内でも高品質なプロンプト生成が可能。**

両者は競合ではなく補完関係:
- **claude.ai**: 人間向け、教育的
- **Antigravity + Skill**: 機械処理向け、工学的

---

## 使い分け指針

| 目的 | 推奨 |
|:---|:---|
| 人間が読むレビュー報告 | claude.ai |
| CI/CD 統合・自動化 | Antigravity + Skill |
| チーム教育 | claude.ai |

---

## 次のアクション

Prompt-Lang 専用 Skill を作成し、Antigravity 内でのプロンプト生成を強化する。
