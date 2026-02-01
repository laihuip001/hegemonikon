# Mapping ハルシネーション検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `create_session` メソッド内での `JulesSession` コンストラクタ呼び出しにおいて、必須引数 `source` が渡されていない（`# NOTE: Removed self-assignment: source = source` というコメントと共に削除されている）。これにより `TypeError` が発生する。
- `poll_session` メソッド内での `UnknownStateError` コンストラクタ呼び出しにおいて、必須引数 `session_id` が渡されていない。これにより `TypeError` が発生する。
- `_request` メソッド内での `session.request` 呼び出しにおいて、引数 `json` が渡されていない（`# NOTE: Removed self-assignment: json = json` というコメントと共に削除されている）。これによりPOSTリクエスト等でペイロードが送信されない。
- `batch_execute` 内の `bounded_execute` 関数において、`JulesResult` コンストラクタ呼び出し時に `task` 引数が渡されていない。これは必須ではないが（デフォルト値あり）、コンテキスト情報の欠落につながる。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
