# リソースリーク検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **コンテキストマネージャのリエントランシーリーク**: `__aenter__` メソッドがネストされた呼び出しを考慮していません。すでに `_owned_session` が存在する場合でも新しいセッションを作成して上書きしてしまうため、古いセッションがクローズされずにリークします。
- **ポート枯渇リスク**: クライアントがコンテキストマネージャとして使用されない場合、`poll_session` 内のループで `get_session` が呼ばれるたびに新しい `aiohttp.ClientSession` が作成・破棄されます。高い並行数（MAX_CONCURRENT=60）でポーリングを行うと、短期間に大量の TCP 接続が TIME_WAIT 状態となり、ポート枯渇を引き起こす可能性があります。
- **UnknownStateError の引数不足**: `poll_session` 内で `UnknownStateError` を送出する際、必須引数である `session_id` が渡されていません（`# NOTE: Removed self-assignment` というコメントと共に削除されています）。これにより例外処理自体が失敗します。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
