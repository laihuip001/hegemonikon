# 音節数の作曲家 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `retryable_exceptions` (7音節): 発音困難。`retry_on` (3音節) などへの短縮を検討。 (Low)
- `use_global_semaphore` (7音節): 長すぎる。`use_global` (3音節) または `shared_lock` (2音節) 等。 (Low)
- `consecutive_unknown` (6音節): 認知負荷が高い。`unknown_count` (3音節) が望ましい。 (Low)
- `synedrion_review` (5音節): `full_review` (3音節) など。 (Low)
- `RateLimitError` (5音節): `LimitError` (4音節) または `RateError` (3音節)。 (Low)
- `UnknownStateError` (5音節): `StateError` (3音節)。 (Low)
- `initial_delay` (5音節): `start_wait` (2音節)。 (Low)
- `automation_mode` (5音節): `auto_mode` (3音節)。 (Low)
- `bounded_execute` (5音節): `safe_run` (2音節)。 (Low)
- `backoff_factor` (4音節): `backoff` (2音節) で十分。 (Low)
- `create_session` (4音節): `new_session` (3音節) や `start` (1音節)。 (Low)
- `create_and_poll` (4音節): `run_task` (2音節)。 (Low)
- `batch_execute` (4音節): `batch_run` (2音節)。 (Low)
- `progress_callback` (4音節): `on_progress` (3音節)。 (Low)
- `mask_api_key` (4音節): `mask_key` (2音節)。 (Low)

## 重大度
Low
