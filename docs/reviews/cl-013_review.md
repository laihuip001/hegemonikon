# エラーハンドリング一貫性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **戻り値パターンの不一致**: 単一操作メソッド（`create_and_poll`等）は例外を送出するが、バッチ操作メソッド（`batch_execute`）は例外を捕捉し、`JulesResult`オブジェクト（`is_success`/`is_failed`プロパティ付き）を返す。呼び出し元はメソッドによって異なるエラー処理ロジックを実装する必要がある。
- **例外階層の混合**: カスタム例外（`JulesError`, `RateLimitError`）と標準例外（`TimeoutError`, `ValueError`）、およびライブラリ例外（`aiohttp.ClientError`）が混在している。これにより、呼び出し元での包括的なエラー捕捉が困難になっている。
- **重複したリトライ/バックオフ制御**: `get_session`メソッドは`@with_retry`デコレータでリトライ制御されているが、呼び出し元の`poll_session`でも`RateLimitError`を捕捉して独自のバックオフ制御を行っている。これにより意図しない長時間待機が発生する可能性がある。
- **エラー情報のデータ型不整合**: `JulesSession.error`フィールドは、APIからのレスポンス（文字列）の場合と、Python例外の文字列表現（`str(e)`）の場合が混在している。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
