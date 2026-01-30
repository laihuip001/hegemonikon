# 入力検証欠落検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `create_session` メソッドにおいて、`prompt` および `source` 引数が空文字列または None でないかの検証が欠落しています。
- `get_session` メソッドにおいて、`session_id` 引数が空文字列でないかの検証が欠落しています。
- `poll_session` メソッドにおいて、`timeout` および `poll_interval` 引数が正の整数であるかの検証が欠落しています。
- `batch_execute` メソッドにおいて、`tasks` リスト内の各要素が必須キー（`prompt`, `source`）を持つ辞書であるかの検証が欠落しています。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
