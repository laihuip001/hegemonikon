---
doc_id: "ANTIGRAVITY_RULES_SKILLS_GUIDE"
source: "Perplexity AI"
date: "2026-01-21"
topic: "Antigravity Rules/Skills 適用モードと Context Rot 対策"
---

# Antigravity + Claude における Rules / Skills / Context rot 実務ガイド

## 1. Rules の適用モード

| モード | 動作 | 用途 |
|--------|------|------|
| **Always On** | 毎ターンシステムプロンプトに注入 | 常に守るべき制約 |
| **Manual** | 明示的呼び出し時のみ有効 | テスト用、特定フェーズ用 |
| **Model Decision** | AIが関連性を判定して適用 | 抜けやすい、非推奨 |

### 設定方法
Settings → Customizations → Manage → Rules タブ → Activation Mode を変更

---

## 2. Skills の確実な発火

### SKILL.md の書き方

```yaml
---
name: "code-review"
description: >
  Use when: ユーザーが「コードレビュー」「コードを見て」「レビューして」と言った時。
---

## When Activated
- 「コードレビューして」
- `/review` コマンド
```

### 強制発火フレーズ
- 「必ず skill `code-review` を使って〜」
- 「Use skill `<name>` to ...」

---

## 3. Context Rot 対策

| 対策 | 詳細 |
|------|------|
| ファイルに責務を逃がす | 方針はファイルに固定、チャットで参照 |
| フェーズ分割 | 1トピック/1マイルストーンでスレッド分割 |
| 要約引き継ぎ | フェーズ終了時に要約を作り新スレに渡す |
| ルールを短く | 長文ルールは逆効果、上位概念のみ |

---

## 4. 推奨構成

| ファイル | モード | 内容 |
|----------|--------|------|
| `GEMINI.md` (Global) | Always On | 言語・トーン・安全ポリシー |
| `.agent/rules/*.md` (Workspace) | Always On | プロジェクト固有ルール |
| `.agent/skills/*/SKILL.md` | 自動 | トリガー条件を明確に記述 |

---

*Source: Perplexity AI, 2026-01-21*
