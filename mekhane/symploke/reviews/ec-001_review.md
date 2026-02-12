# 空入力恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `create_session` メソッドの `prompt` 引数が空文字列の場合のチェックがありません。(High)
- `create_session` メソッドの `source` 引数が空文字列の場合のチェックがありません。(High)
- `get_session` メソッドの `session_id` 引数が空文字列の場合のチェックがありません。(High)

## 重大度
High
