# エラーハンドリング一貫性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **例外のカプセル化不足 (Leaky Abstractions)**: `_request` メソッド内で `resp.raise_for_status()` を使用しているため、HTTPエラー発生時に `aiohttp.ClientResponseError` がそのまま外部に送出される。利用者がこのクライアントを使用する際、`aiohttp` の例外仕様を把握・依存する必要がある。`JulesError` 等の独自例外にラップすべきである。
- **リトライロジックの重複 (Duplicated Retry Logic)**: `@with_retry` デコレータと `poll_session` メソッド内で、それぞれ独立して「指数バックオフ」と「RateLimitError時の `Retry-After` ヘッダー処理」が実装されている。ロジックが重複しており、保守性が低下している。
- **エラーハンドリングの一貫性 (Error Handling Consistency)**: `batch_execute` 内の `bounded_execute` は `Exception` をキャッチして失敗ステータスの `JulesSession` を返すが、単体実行メソッド (`create_session`, `poll_session`) は例外を送出する。バッチ処理の特性上理解できるが、エラー情報の取得方法が「例外キャッチ」と「戻り値のプロパティ確認」に二分されている。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
