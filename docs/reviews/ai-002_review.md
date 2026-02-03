# Mapping ハルシネーション検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **存在しないAPIエンドポイント**: `BASE_URL` が `https://jules.googleapis.com/v1alpha` に設定されていますが、Google Jules API は存在しません。
- **メソッド呼び出しにおける引数欠落 (自己代入の誤認による削除)**:
    - `_request` メソッド内の `session.request` 呼び出しで `json` 引数が削除されています (L200: `# NOTE: Removed self-assignment: json = json`)。これにより、JSONペイロードが送信されません。
    - `create_session` メソッド内の `JulesSession` コンストラクタ呼び出しで `source` 引数が削除されています (L244: `# NOTE: Removed self-assignment: source = source`)。`source` は必須引数のため、`TypeError` が発生します。
    - `poll_session` メソッド内の `UnknownStateError` コンストラクタ呼び出しで `session_id` 引数が削除されています (L299: `# NOTE: Removed self-assignment: session_id = session_id`)。`session_id` は必須引数のため、`TypeError` が発生します。
    - `batch_execute` メソッド内の `JulesResult` コンストラクタ呼び出しで `task` 引数が削除されています (L384: `# NOTE: Removed self-assignment: task = task`)。これにより、エラー時にタスク情報が失われます。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
