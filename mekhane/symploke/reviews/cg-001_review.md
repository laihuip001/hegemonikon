# ネスト深度警報者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `with_retry` デコレータ内の `wrapper` 関数にて、ネストが5段に達しています (High)。
  - `wrapper` -> `for` -> `try` -> `except` -> `if`
- `poll_session` メソッドにて、ネストが4段に達しています (High)。
  - `while` -> `try` -> `if` -> `if`

## 重大度
High
