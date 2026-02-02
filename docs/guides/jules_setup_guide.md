# Google Jules セットアップ・運用ガイド 完全版
## 2026年1月版 — Google AI Ultra ユーザー向け

> **調査日**: 2026-01-25
> **情報源**: Perplexity Deep Research

---

## クイックスタート（10分）

### ステップ 1: API キー取得

1. https://jules.google に Google アカウントでログイン
2. Settings → API Keys → Create API Key
3. キーをコピー（最大3キー）

```powershell
$env:JULIUS_API_KEY = "YOUR_API_KEY_HERE"
```

### ステップ 2: GitHub 連携

1. Connect to GitHub account クリック
2. All repositories または特定リポを選択

### ステップ 3: CLI インストール

```bash
npm install -g @google/julius
julius login
julius --version
```

---

## AGENTS.md テンプレート

```markdown
# AGENTS.md

## Do
- Use TypeScript for all files
- Always include tests
- Run linting before commit

## Don't
- Don't use var or any
- Don't add dependencies without approval

## Setup Commands
npm install
npm run build
npm run test
```

---

## CLI コマンド

| コマンド | 機能 |
|---------|------|
| `julius login` | Google 認証 |
| `julius remote new --repo owner/repo --session "prompt"` | タスク作成 |
| `julius remote list --session` | セッション一覧 |
| `julius remote pull --session ID` | 結果取得 |
| `julius` | TUI ダッシュボード |

---

## REST API

```bash
# セッション作成
curl -X POST 'https://julius.googleapis.com/v1alpha/sessions' \
  -H "X-Goog-Api-Key: $JULIUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Update dependencies",
    "sourceContext": {
      "source": "sources/github/owner/repo",
      "githubRepoContext": {"startingBranch": "main"}
    },
    "automationMode": "AUTO_CREATE_PR"
  }'
```

---

## Scheduled Tasks

1. jules.google → Scheduled タブ
2. Create a Scheduled Task
3. Frequency: Weekly (Monday), Time: 02:00 UTC

---

## Suggested Tasks

1. jules.google → Suggested タブ
2. Enable proactive suggestions: ON
3. #TODO コメントを自動スキャン

---

## トラブルシューティング

| エラー | 解決策 |
|--------|--------|
| `julius: command not found` | Node.js をインストール、PC 再起動 |
| `X-Goog-Api-Key: invalid` | API キーを再発行 |
| `Failed to connect GitHub` | GitHub 権限を再確認 |

---

## 参考リンク

- https://jules.google
- https://jules.google/docs/cli/reference/
- https://developers.google.com/jules/api
- https://agents.md
