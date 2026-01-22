---
description: 承認済み計画を実行開始するトリガー。「今やれ」の明示的指示。
hegemonikon: Praxis-H
modules: [M6, M2]
---

# /do: 実行開始プロトコル

> **Hegemonikón Module**: M6 Praxis (実行) + M2 Krisis (判断)

> **目的**: 承認済みの計画を「今この瞬間から」実行開始する
> **前提条件**: `/plan` が完了し、ユーザー承認 (`y`) を得ていること

---

## `/do` の位置づけ

```
/plan → 計画作成 → y (承認) → /do (実行開始)
```

| 操作 | 意味 | 状態遷移 |
|------|------|----------|
| `y` | 計画承認 — 設計に同意 | PLANNING → APPROVED |
| `/do` | 実行開始 — 今すぐやれ | APPROVED → EXECUTION |

> [!NOTE]
> `y` と `/do` は分離されている。承認後、すぐに実行しなくても良い。
> 別の作業を挟んでから `/do` で再開することも可能。

---

## 前提条件確認

> [!WARNING]
> 計画が APPROVED 状態でない場合、エラーを返す。

確認事項:
- [ ] `implementation_plan.md` が作成済み
- [ ] ユーザーから `y`（承認）を得ている
- [ ] APPROVED 状態である

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

---

## Step 3: 納品

1. 変更サマリーを作成
2. コミットメッセージ案を提示（Conventional Commits形式）
3. 必要に応じて `walkthrough.md` を更新

---

## Step 4: Memory Logging (Auto)

実行完了を自己記録する:
```bash
python forge/gnosis/logger.py log "system" "/do Completed" --session "AutoLog"
```

---

## 出力形式

```
┌─[Hegemonikón]──────────────────────┐
│ M6 Praxis: 実行開始               │
│ 計画: implementation_plan.md       │
│ M2 Krisis: 優先度判断完了         │
│ 実行: [N]ファイル変更              │
│ リスク: [Low/Medium/High]          │
└────────────────────────────────────┘

✅ /do 完了

## 変更サマリー
- `path/to/file1.py`: [変更内容]
- `path/to/file2.ts`: [変更内容]

## テスト結果
[パス/失敗の状況]

## コミットメッセージ案
feat(scope): description

⏸️ 次のステップ: コミットしますか？
```
