# エラーハンドリング一貫性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **実装詳細の漏洩 (Leakage of Implementation Details)**: `aiohttp.ClientError` が公開インターフェース（デコレータのデフォルト引数）や例外としてそのまま露出しています。これにより、クライアント利用者が `aiohttp` に依存することになります。`JulesNetworkError` 等の独自の例外でラップすることが望ましいです。
- **例外階層の不統一 (Inconsistent Exception Hierarchy)**: `RateLimitError` や `UnknownStateError` は独自の基底クラス `JulesError` を継承していますが、タイムアウト時は標準ライブラリの `TimeoutError` を送出しています。一貫性を保つため、`JulesError` を継承した `JulesTimeoutError` の導入が推奨されます。
- **リトライとバックオフの重複 (Redundant Retry/Backoff)**: `poll_session` メソッド内で、`get_session`（`@with_retry` によりリトライ機能付き）を呼び出しつつ、さらに `poll_session` 自身も `RateLimitError` に対するバックオフとループを持っています。これにより、レート制限発生時に「短期間の3回リトライ」と「長期間のバックオフ」が複雑に組み合わさる挙動となっています。
- **バッチ処理の例外処理 (Robust Batch Error Handling)**: `batch_execute` における例外処理は、`Exception` をキャッチして `JulesResult` にエラー情報を格納する設計となっており、バッチ全体の停止を防ぐ適切なパターン（Bulkhead pattern）が適用されています。また、`CancelledError` が Python 3.8+ で `Exception` に含まれない点を考慮している点も堅牢です。

## 重大度
- Low

## 沈黙判定
- 発言（要改善）
