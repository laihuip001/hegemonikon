# コード/コメント矛盾検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- **Critical**: `_request` メソッド内で `json` 引数が `session.request` に渡されていない。コメント `# NOTE: Removed self-assignment: json = json` は誤りで、これにより POST リクエストのペイロードが送信されない。
- **Critical**: `create_session` メソッド内で `JulesSession` コンストラクタに `source` 引数が渡されていない。コメント `# NOTE: Removed self-assignment: source = source` は誤りで、`TypeError` が発生する。
- **Critical**: `poll_session` メソッド内で `UnknownStateError` コンストラクタに `session_id` 引数が渡されていない。コメント `# NOTE: Removed self-assignment: session_id = session_id` は誤りで、`TypeError` が発生する。
- **High**: `batch_execute` メソッド内で `JulesResult` コンストラクタに `task` 引数が渡されていない。コメント `# NOTE: Removed self-assignment: task = task` は誤りで、エラー時にタスク情報が失われる。

## 重大度
Critical
