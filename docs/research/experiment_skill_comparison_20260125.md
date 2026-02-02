# 公平な再実験: 3者比較（Skill 適用）

**日時**: 2026-01-25 08:40
**課題**: API ドキュメント生成用システムプロンプト（Prompt-Lang v2 形式）
**条件**: 全員に meta-prompt-generator Skill の設計原則を適用

---

## 結果サマリー

| AI | Phase 0 実施 | @rubric | @if | @examples | 評価 |
|:---|:---|:---:|:---:|:---:|:---:|
| Antigravity Claude | 自己完結 | 4次元 | 2 | 1 | ⭐⭐⭐⭐ |
| claude.ai | 自己完結 | 4次元 | 4 | 2 | ⭐⭐⭐⭐⭐ |
| **Web Jules** | **対話的** | 5段階 | 1 | 1 | ⭐⭐⭐⭐⭐ |

---

## 重要な発見

### 1. Skill は「品質の底上げ装置」

| Skill なし | Skill あり |
|:---|:---|
| 大きな品質差 | **3者とも高品質** |

### 2. 各 AI の個性

| AI | 個性 |
|:---|:---|
| claude.ai | 網羅的、Pre-Mortem 付き |
| Jules | 対話的、「Never Hallucinate」強調 |
| Antigravity Claude | 簡潔、実装寄り |

### 3. Jules の「対話的」Phase 0

Jules は Phase 0 をユーザーと一緒に行う設計。
これは設計思想の違いであり、**より正確な要件反映**につながる。

---

## 結論

**Skill を渡せば、どの AI でもプロンプト生成に使える。**

| 用途 | 推奨 |
|:---|:---|
| 最大詳細度 | claude.ai |
| 対話的な要件定義 | Jules |
| 簡潔・高速 | Antigravity Claude |
