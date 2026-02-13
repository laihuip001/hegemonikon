# ネスト深度警報者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `with_retry` (L191-201): `for` -> `try` -> `if/else` (深度5) [High]
- `_request` (L338-346): `try` -> `async with` -> `if` (深度4) [High]
- `poll_session` (L452-473): `while` -> `try` -> `if` -> `if` (深度5) [High]
- `batch_execute.bounded_execute` (L532-542): `async with` -> `try` -> `await` (深度5) [High]

## 重大度
High
