# 入力検証欠落検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `create_session` メソッドにて、`prompt` (タスク説明) が空でないことの検証が欠落しています。
- `create_session` メソッドにて、`source` (リポジトリソース) の形式検証 (例: "sources/github/..." で始まるか) および空チェックが欠落しています。
- `get_session` メソッドにて、`session_id` が空でないことの検証が欠落しています。空文字列の場合、意図しないエンドポイント (`.../sessions/`) へのリクエストとなります。
- `poll_session` メソッドにて、`timeout` および `poll_interval` が正の数値であることの検証が欠落しています。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
