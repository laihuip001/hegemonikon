# 再試行ロジック評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **Jitter（ゆらぎ）の欠如**: `with_retry` デコレータおよび `poll_session` メソッドのバックオフ計算にランダムな要素（Jitter）が含まれていません。複数のクライアントが同時にレート制限に達した場合、同時に再試行を行い、Thundering Herd 問題を引き起こすリスクがあります。
- **`Retry-After` ヘッダー解析の脆弱性**: `_request` メソッド内で `int(retry_after)` を使用していますが、RFC 7231 では HTTP 日付形式も許容されています。整数以外の値が返された場合、`ValueError` が発生し、適切なバックオフ処理が行われない可能性があります。
- **過剰な再試行対象**: `with_retry` のデフォルト引数 `retryable_exceptions` に `aiohttp.ClientError` が含まれています。これにより、`raise_for_status()` で発生する 400 (Bad Request), 404 (Not Found) 等のクライアントエラーも再試行対象となってしまいます。これらは通常、再試行しても解決しないため、リソースの無駄遣いとなります（5xx エラーや接続エラーに限定すべきです）。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
