# 戻り値詐欺検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `create_session` メソッドは `JulesSession` を返すと宣言されているが、実装では `JulesSession` コンストラクタ呼び出し時に必須引数 `source` が欠落しており、`TypeError` が発生するため、宣言された型を返さない。(Critical)
- `poll_session` メソッドは `UnknownStateError` を送出するコードパスがあるが、例外の初期化時に必須引数 `session_id` が欠落しており、`TypeError` が発生する。意図した例外型と異なる。(High)
- `_request` メソッドは `json` 引数を受け取るが、内部の `session.request` 呼び出しでその引数を使用していない（コメントで削除されている）。これにより意図したリクエストが送信されず、期待される戻り値が得られない可能性がある。(High)
- `batch_execute` メソッド内の例外処理ブロックで `JulesResult` を返す際、`task` 引数が渡されていない。`JulesResult` の定義では `task` にデフォルト値があるため型エラーではないが、情報の欠落が発生している。(Medium)

## 重大度
Critical
