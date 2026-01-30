# エラーハンドリング一貫性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **aiohttp例外の漏洩**: `_request` メソッド内で `resp.raise_for_status()` を使用しており、APIエラー時に `aiohttp.ClientResponseError` がそのまま呼び出し元に伝播しています。これは抽象化の漏れであり、呼び出し元が `aiohttp` に依存する必要があります。ドメイン固有の例外（例: `JulesAPIError`）でラップすべきです。
- **例外型の不統一**: `poll_session` メソッドでタイムアウト時に標準の `TimeoutError` を送出しています。`JulesError` を継承した `JulesTimeoutError` 等を使用する方が、ライブラリ固有のエラーハンドリングとして一貫性があります。
- **単一操作とバッチ操作の挙動不一致**: `create_session` 等の単一操作メソッドは例外を送出する一方、`batch_execute` は例外を捕捉して `JulesResult` オブジェクト（失敗状態のセッションを含む）を返します。バッチ処理において全停止を防ぐための一般的なパターンですが、利用者がこの違いを意識する必要があります。
- **エラー時の擬似セッション生成**: `batch_execute` でエラーが発生した際、ランダムなUUIDを持つ `JulesSession` を生成し `SessionState.FAILED` として返しています。これは実在しないセッションIDを生成するため、追跡やデバッグ時に混乱を招く可能性があります。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
