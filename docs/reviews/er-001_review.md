# 例外メッセージの詩人 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `UnknownStateError` のメッセージ ("Unknown session state 'X' for session Y") には、ユーザーが取るべき行動（対処法）が含まれていません (Medium)
- `TimeoutError` のメッセージ ("Session X did not complete within Ys") には、タイムアウトを延長するなどの具体的な対処法が含まれていません (Medium)
- `resp.raise_for_status()` によって発生する `aiohttp.ClientResponseError` は技術的な詳細のみを含み、ユーザーへの文脈や対処法が不足しています (Medium)
- `RateLimitError` のメッセージ ("Rate limit exceeded for X") は原因を示していますが、具体的な待機や再試行の指示（アクション）がメッセージテキストに含まれていません (Medium)

## 重大度
Medium
