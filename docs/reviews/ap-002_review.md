# ステータスコード裁判長 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- 不適切な4xx系の再試行 (High): `with_retry` デコレータが `aiohttp.ClientError` を無差別に再試行対象としているため、`raise_for_status()` で発生する 4xx クライアントエラー（400 Bad Request, 404 Not Found 等）も再試行されます。これらはクライアント側の恒久的な誤りであり、一時的な障害（5xx系）として扱うべきではありません。ステータスコードの意味論を無視しています。

## 重大度
High
