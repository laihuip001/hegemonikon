# DRY違反検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **API Base URLの重複定義**: `JulesClient.BASE_URL` ("https://jules.googleapis.com/v1alpha") が `mekhane/symploke/run_specialists.py` および `mekhane/symploke/tests/test_api_connection.py` にハードコードされており、3箇所で重複している。
- **HTTPヘッダー構築ロジックの重複**: `{"X-Goog-Api-Key": ..., "Content-Type": "application/json"}` というヘッダー定義が、上記3ファイルすべてで同一の形式で記述されている。
- **セッション管理ロジックの再実装**: `mekhane/symploke/run_specialists.py` が `JulesClient` を使用せず、`create_session` やポーリングロジックを独自に再実装している。これにより、`JulesClient` の持つリトライ処理やエラーハンドリングが活用されていない。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
