# ブール命名の審判 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `OTEL_AVAILABLE` (Global Constant): 接頭辞欠如 (Medium)
- `close_after` (Local Variable in `_request`): 接頭辞欠如 (Medium)
- `auto_approve` (Argument in `create_session`): 接頭辞欠如 (Medium)
- `fail_on_unknown` (Argument in `poll_session`): 接頭辞欠如 (Medium)
- `use_global_semaphore` (Argument in `batch_execute`): 接頭辞欠如 (Medium)

## 重大度
Medium
