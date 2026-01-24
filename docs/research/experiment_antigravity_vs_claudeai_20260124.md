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
| Antigravity（Skillなし） | 簡潔・実装寄り | △ |
| Antigravity（meta-prompt-generator Skill適用） | 体系的・工学的・Precision特化 | ✅ |
| claude.ai | 汎用・教育的・人間向け | ✅ |

---

## 主要な違い

| 観点 | claude.ai | Antigravity + Skill |
|:---|:---|:---|
| 設計思想 | バランス型 | Precision特化 |
| 出力形式 | Markdown（人間向け） | JSON（機械処理向け） |
| 確信度 | なし | 0.0-1.0定量化 |
| CVSSスコア | なし | 完全対応 |
| Fallback | なし | 明示定義 |

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
