# fail-fast伝道者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `create_session` において、引数 `prompt` や `source` の空文字チェックなどの検証が行われていません。無効な入力でもリクエストを送信してしまいます。（Late Validation）: High
- `batch_execute` において、`tasks` リスト内の各辞書が必須キー（`prompt`, `source`）を含んでいるかどうかの事前検証がありません。実行時（非同期処理中）に `KeyError` が発生するまで問題が発覚しません。（Late Validation）: High
- `get_session` において、`session_id` の必須チェック（空文字チェックなど）が欠如しています。: Medium

## 重大度
High
