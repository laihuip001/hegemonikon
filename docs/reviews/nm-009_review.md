# 定数命名の番人 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- (Medium) `__aenter__` メソッド内の `keepalive_timeout=30` がマジックナンバーとして放置されている。`KEEPALIVE_TIMEOUT` 定数にすべき。
- (Medium) `_request` メソッド内の `body[:200]` がマジックナンバーとして放置されている。`ERROR_LOG_PREVIEW_LENGTH` 等の定数にすべき。
- (Medium) `poll_session` メソッド内の `consecutive_unknown >= 3` がマジックナンバーとして放置されている。`MAX_UNKNOWN_STATE_RETRIES` 定数にすべき。
- (Medium) `poll_session` メソッド内の `min(current_interval * 2, 60)` の `60` がマジックナンバーとして放置されている。`MAX_POLL_BACKOFF` 定数にすべき。
- (Low) `mask_api_key` 関数内の `visible_chars * 2 + 4` の `4` がマジックナンバーとして放置されている。
- (Low) `batch_execute` メソッド内の `uuid.uuid4().hex[:8]` の `8` がマジックナンバーとして放置されている。

## 重大度
Medium
