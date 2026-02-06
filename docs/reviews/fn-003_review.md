# 引数数の門番 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `with_retry` (L154): 引数が5個ある (`max_attempts`, `backoff_factor`, `initial_delay`, `max_delay`, `retryable_exceptions`) - High
- `JulesClient.create_session` (L354): 引数が5個ある (`prompt`, `source`, `branch`, `auto_approve`, `automation_mode`) - High
- `JulesClient.synedrion_review` (L591): 引数が5個ある (`source`, `branch`, `domains`, `axes`, `progress_callback`) - High

## 重大度
High
