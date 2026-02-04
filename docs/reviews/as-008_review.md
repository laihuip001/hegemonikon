# コネクションプール評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **ポーリング時の非効率な接続管理**: `poll_session` メソッドは `get_session` を繰り返し呼び出しますが、`JulesClient` がコンテキストマネージャー (`async with`) として使用されていない場合、各リクエストごとに新しい `aiohttp.ClientSession` が作成・破棄されます。これにより、TCPハンドシェイクのオーバーヘッドが発生し、Keep-Alive が機能しません。ドキュメントの記載例もコンテキストマネージャーを使用していません。
- **適切なプール設定**: コンテキストマネージャーとして使用された場合 (`__aenter__`) は、`aiohttp.TCPConnector` を `limit=MAX_CONCURRENT` および `keepalive_timeout=30` で適切に初期化しており、リソース制限と接続再利用が正しく実装されています。
- **並行数制御の整合性**: `batch_execute` で使用される `_global_semaphore` の制限値が接続プールの `limit` と一致しており、プール枯渇を防ぐ設計になっています。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
