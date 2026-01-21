---
description: 承認済み計画に基づく実装プロトコル。計画駆動開発の実行フェーズ。
hegemonikon: Praxis-H
modules: [M6, M2]
---

# /code: 実装プロトコル

> **Hegemonikón Module**: M6 Praxis (実行) + M2 Krisis (判断)

> **目的**: 承認済みの計画に基づいてコードを実装し、検証する
> **前提条件**: `/plan` が完了し、ユーザー承認を得ていること

---

## 前提条件確認

以下のいずれかが存在することを確認:

- [ ] `implementation_plan.md` が作成済み
- [ ] `/plan` でプランが承認済み
- [ ] ユーザーからの明示的な実装開始指示

> [!WARNING]
> 承認なしでこのワークフローを開始してはならない。

---

## Step 1: 反復実装

1. 計画書の各ファイルについて順次実装
2. ファイルごとに以下を実行:
   - 対象ファイルを読み込む（存在する場合）
   - 変更を適用または新規作成
   - **Self-Audit**: `.agent/rules/` への違反がないか確認

### Self-Audit チェックリスト

各ファイル編集後に確認:

- [ ] Protocol G: Git操作を直接実行していないか
- [ ] Protocol D: 外部サービスを検証せずに推奨していないか
- [ ] Protocol V: バージョン番号を未検証で出力していないか
- [ ] Safety Invariants: 機密情報を露出していないか

---

## Step 2: 検証

1. 単体テストを作成（テストファーストを推奨）
2. テストを実行
3. 失敗した場合は修正ループに入る

### テスト実行コマンド例

```bash
# Python
pytest tests/ -v

# JavaScript/TypeScript
npm test

# Go
go test ./...
```

---

## Step 3: 納品

1. 変更サマリーを作成
2. コミットメッセージ案を提示（Conventional Commits形式）
3. 必要に応じて `walkthrough.md` を更新

### コミットメッセージ形式

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

| Type | 説明 |
|------|------|
| feat | 新機能 |
| fix | バグ修正 |
| docs | ドキュメント |
| refactor | リファクタリング |
| test | テスト追加 |
| chore | その他 |

---

## Step 4: Memory Logging (Auto)

実装完了を自己記録する:
```bash
python forge/gnosis/logger.py log "system" "/code Completed" --session "AutoLog"
```

---

## 出力形式

```
┌─[Hegemonikón]──────────────────────┐
│ M6 Praxis: 実行判断完了           │
│ 計画: implementation_plan.md       │
│ M2 Krisis: 優先度判断完了         │
│ 実行: [N]ファイル変更                │
│ リスク: [Low/Medium/High]           │
└────────────────────────────────────┘

✅ /code 完了

## 変更サマリー
- `path/to/file1.py`: [変更内容]
- `path/to/file2.ts`: [変更内容]

## テスト結果
[パス/失敗の状況]

## コミットメッセージ案
feat(auth): implement OAuth2 authentication flow

- Add OAuth2 provider abstraction
- Implement Google OAuth2 handler
- Add session management

⏸️ 次のステップ: コミットしますか？
```
