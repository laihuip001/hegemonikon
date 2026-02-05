# 入力検証欠落検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `create_session` メソッドにおいて、`prompt` および `source` 引数が空文字列または `None` でないかの検証が欠落している。
- `batch_execute` メソッドにおいて、`tasks` リスト内の辞書が必須キー（`prompt`, `source`）を含んでいるかの事前検証がない。実行時の `KeyError` に依存している。
- `poll_session` メソッドにおいて、`timeout` および `poll_interval` が正の数値であるかの検証がない。
- `_request` メソッドにおいて、`method` が有効なHTTPメソッドであるかの検証がない。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
