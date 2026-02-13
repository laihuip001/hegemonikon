# 定数命名の番人 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- マジックナンバーの放置 (Medium): `30` (L217: `keepalive_timeout=30`) - 定数化すべきです（例: `KEEPALIVE_TIMEOUT`）
- マジックナンバーの放置 (Medium): `200` (L267: `body[:200]`) - 定数化すべきです（例: `ERROR_LOG_BODY_LIMIT`）
- マジックナンバーの放置 (Medium): `3` (L343: `consecutive_unknown >= 3`) - 定数化すべきです（例: `MAX_UNKNOWN_RETRIES`）
- マジックナンバーの放置 (Medium): `60` (L353: `min(current_interval * 2, 60)`) - 定数化すべきです（例: `MAX_POLL_BACKOFF`）
- マジックナンバーの放置 (Medium): `4` (L527, L536: `visible_chars * 2 + 4`) - 定数化すべきです（例: `MIN_MASK_BUFFER`）

## 重大度
Medium
