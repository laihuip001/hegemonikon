# ネスト深度警報者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `with_retry` デコレータ内の `wrapper` 関数において、ループ、トライ、条件分岐が重なり、ネスト深度が5に達しています (Severity: High)
- `poll_session` メソッドにおいて、ループ、トライ、条件分岐が重なり、ネスト深度が5に達しています (Severity: High)
- `batch_execute` メソッド内の内部関数 `bounded_execute` において、`async with` ブロックと `try` ブロックにより、ネスト深度が4に達しています (Severity: High)

## 重大度
High
