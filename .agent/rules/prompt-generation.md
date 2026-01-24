---
description: .prompt ファイル編集時のプロンプト生成ルール
activation: glob
pattern: "**/*.prompt"
priority: 1
hegemonikon: Taxis
---

# Prompt-Lang 編集ルール

> **適用条件**: `.prompt` 拡張子のファイルを編集・作成する際に自動適用

## 構文ルール

### 必須ディレクティブ
1. `#prompt <name>` — ファイル先頭でプロンプト名を宣言
2. `@role:` — LLMの役割を定義
3. `@goal:` — 達成すべき目標を明示

### 推奨ディレクティブ
- `@constraints:` — 禁止事項・制約条件
- `@format:` — 出力形式（JSON Schema推奨）
- `@examples:` — Few-shot例（3-5個推奨）

### v2 ディレクティブ（オプション）
- `@rubric:` — 自己評価指標
- `@activation:` — Glob/ルール連携メタデータ
- `@if/@else/@endif` — 条件分岐

## 品質基準

### 曖昧さ排除
- ❌ 「いい感じにして」「適切に」「必要に応じて」
- ✅ 具体的な条件・数値・形式を明示

### 構造化
- 各ディレクティブは2スペースインデント
- リスト項目は `  - ` で開始
- コードブロックは ` ``` ` で囲む

## 参照

- [Prompt-Lang v2 仕様書](file:///M:/Hegemonikon/docs/specs/prompt-lang-v2-spec.md)
- [統合研究レポート](file:///M:/Hegemonikon/docs/research/prompt-lang-complete-report.md)
