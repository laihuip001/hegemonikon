# 定数命名の番人 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `JulesClient.__aenter__` (L231): `keepalive_timeout=30` の `30` がマジックナンバーとして放置されています。`KEEPALIVE_TIMEOUT` などの定数にすべきです。(Medium)
- `JulesClient.poll_session` (L347): `consecutive_unknown >= 3` の `3` がマジックナンバーとして放置されています。`MAX_UNKNOWN_RETRIES` などの定数にすべきです。(Medium)
- `JulesClient.poll_session` (L360): バックオフ上限値 `60` がマジックナンバーとして放置されています。`MAX_BACKOFF_DELAY` などの定数にすべきです。(Medium)
- `mask_api_key` (L553): `visible_chars * 2 + 4` の `4` がマジックナンバーとして放置されています。`MIN_MASK_LENGTH_OFFSET` などの定数にすべきです。(Medium)

## 重大度
Medium
