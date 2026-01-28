# コネクションプール評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `create_session` および `get_session` メソッド内で、呼び出しのたびに `aiohttp.ClientSession()` を新規に作成している。
- これにより、HTTP接続の再利用（Keep-Alive）が行われず、リクエストごとにTCP接続確立とSSLハンドシェイクが発生している。
- 特に `poll_session` メソッドではループ内で `get_session` を繰り返し呼び出すため、ポーリング間隔ごとに不要な接続オーバーヘッドが発生し、クライアントおよびサーバーのリソースを浪費している。
- `aiohttp` のベストプラクティスに従い、`ClientSession` は `JulesClient` のインスタンス生成時に一度だけ作成し、インスタンス全体で共有すべきである。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
