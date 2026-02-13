# 空入力恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `create_session` の `prompt` 引数が空文字列の場合の検証がない (High)
- `create_session` の `source` 引数が空文字列の場合の検証がない (High)
- `get_session` の `session_id` 引数が空文字列の場合の検証がない (High)

## 重大度
High
