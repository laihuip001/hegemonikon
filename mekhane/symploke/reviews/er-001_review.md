# 例外メッセージの詩人 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `RateLimitError` (Medium): メッセージ "Rate limit exceeded" に原因（例: トラフィック過多）と対処法（例: retry_after秒後にリトライしてください）が含まれていない。
- `UnknownStateError` (Medium): メッセージ "Unknown session state '{state}' for session {session_id}" に対処法（例: クライアントライブラリの更新を確認してください）が含まれていない。
- `TimeoutError` (Medium): `poll_session` メソッド内のメッセージ "Session {session_id} did not complete within {timeout}s" に対処法（例: タイムアウト時間を延ばすか、タスクの状態を確認してください）が含まれていない。

## 重大度
Medium
