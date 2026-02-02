# Walkthrough: Hegemonikón Enhancement Session

**Date**: 2026-01-19

---

## 成果一覧

| 項目 | 内容 |
|------|------|
| `/ask` v2 | ゼロコスト設計、Perplexity/Gemini/ChatGPT対応 |
| Skill実行保証 | Workflow-Module連携追加 |
| 検証義務出力 | 毎回出力モード実装 |
| M1/M2暗黙発動 | `/do`, `/boot` に組込 |
| 診断スクリプト | `.agent/scripts/` に配置 |
| README.md | `.gemini/` 概要ドキュメント作成 |

---

## 変更ファイル

### Workflows

| ファイル | 変更 |
|----------|------|
| `/ask` | ブラウザURL方式デフォルト、API明示オプション化 |
| `/plan` | M4 Phronēsis連携、検証義務出力追加 |
| `/code` | M6 Praxis連携、検証義務出力追加 |
| `/rev` | M7 Dokimē連携（名称変更: /review→/rev） |
| `/hist` | M8 Anamnēsis連携（名称変更: /sync-history→/hist） |
| `/do` | M1/M2発動義務追加 |
| `/boot` | M1+M8連携、出力フォーマット更新 |

### Core Files

| ファイル | 変更 |
|----------|------|
| `GEMINI.md` | Hegemonikón Execution Policy追加 |
| `README.md` | 新規作成 |
| `M5 Peira SKILL.md` | 外部AI連携(ゼロコスト設計)セクション追加 |

### Scripts

| ファイル | 用途 |
|----------|------|
| `diagnose_error.py` | Perplexity/Antigravityエラー診断 |
| `check_environment.py` | 環境設定チェック |

---

## 検証義務出力フォーマット

```
[Hegemonikon] M{N} {Name}
  入力: ...
  判断: ...
  出力: ...
```

---

## 次回セッションへの引継ぎ

1. `/boot` 実行で新形式動作確認
2. Obsidian MCP連携は後日検討
3. 信頼確立後、暗黙発動モードへ切替可能
