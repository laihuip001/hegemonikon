# Mapping ハルシネーション検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **`_request` メソッドにおける `json` 引数の欠落**: 269行付近で `session.request` を呼び出す際、`# NOTE: Removed self-assignment: json = json` というコメントと共に `json` 引数の受け渡しが削除されている。これにより、POSTリクエストなどでペイロードが送信されず、API呼び出しが正常に機能しない。
- **`create_session` メソッドにおける `JulesSession` コンストラクタ引数 `source` の欠落**: 314行付近で `JulesSession` を初期化する際、`# NOTE: Removed self-assignment: source = source` というコメントと共に必須引数 `source` が削除されている。`JulesSession` の定義では `source` は必須であるため、`TypeError` が発生する。
- **`poll_session` メソッドにおける `UnknownStateError` コンストラクタ引数 `session_id` の欠落**: 394行付近で例外を送出する際、`# NOTE: Removed self-assignment: session_id = session_id` というコメントと共に必須引数 `session_id` が削除されている。例外発生時に `TypeError` が発生する。
- **`batch_execute` メソッドにおける `JulesResult` コンストラクタ引数 `task` の欠落**: 477行付近のエラーハンドリングにおいて、`# NOTE: Removed self-assignment: task = task` というコメントと共に `task` 引数が削除されている。これにより、エラー発生時にどのタスクが失敗したかのコンテキスト情報が失われる。
- **存在しないAPIエンドポイント**: `BASE_URL` が `https://jules.googleapis.com/v1alpha` に設定されているが、Google Cloud にこのような公開APIは存在しない可能性が高い（架空のAPIである場合を除く）。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
