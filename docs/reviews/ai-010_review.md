# 入力検証欠落検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `create_session` メソッドにおいて、`prompt` および `source` 引数の空文字チェックや形式検証が行われていません。
- `batch_execute` メソッドにおいて、`tasks` リスト内の辞書が必須キー（`prompt`, `source`）を含んでいるかの検証が事前に実行されていません。実行時に `KeyError` が発生する可能性があります。
- `poll_session` および `create_and_poll` メソッドにおいて、`timeout` や `poll_interval` が正の整数であるかの検証が行われていません。
- `JulesClient` コンストラクタおよび `batch_execute` において、`max_concurrent` が正の整数であるかの検証が行われていません。
- `get_session` および `poll_session` において、`session_id` が空でないことの検証が行われていません。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
