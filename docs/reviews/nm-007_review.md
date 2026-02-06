# ブール命名の審判 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `OTEL_AVAILABLE` (global): 接頭辞 `is_` が欠如しています。 (Medium)
- `close_after` (local variable in `_request`): 接頭辞 `should_` が欠如しています。 (Medium)
- `auto_approve` (argument in `create_session`): 接頭辞 `should_` が欠如しています。 (Medium)
- `fail_on_unknown` (argument in `poll_session`): 接頭辞 `should_` が欠如しています。 (Medium)
- `use_global_semaphore` (argument in `batch_execute`): 接頭辞 `should_` が欠如しています。 (Medium)

## 重大度
Medium
