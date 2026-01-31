# 入力検証欠落検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **`batch_execute` メソッドの入力検証不備**:
    - `tasks` 引数が `list[dict]` として定義されていますが、リスト内の辞書が必須キー（`prompt`, `source`）を含んでいるかどうかの事前検証が行われていません。実行時に `KeyError` が発生する可能性があります。
    - 各タスクの内容（プロンプトの空文字チェックなど）も検証されていません。
- **`create_session` メソッドの入力検証不備**:
    - `prompt` が空文字でないか、`source` が期待される形式（例: `sources/github/...`）であるかの検証がありません。
- **数値パラメータの範囲検証欠落**:
    - `poll_session` の `timeout`, `poll_interval` や、`__init__`, `batch_execute` の `max_concurrent` に対して、正の整数であることの検証（負の値や0のチェック）が含まれていません。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
