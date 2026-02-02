# コネクションプール評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- コンテキストマネージャ（`async with`）を使用しない場合、`_request` メソッドが呼び出しごとに `aiohttp.ClientSession` を新規作成・破棄するため、コネクションプーリングが機能しません。特に `poll_session` メソッドのようなループ処理において、都度 TCP/TLS ハンドシェイクが発生し、非効率かつサーバー負荷が高まります。
- `__aenter__` における `TCPConnector` の設定（`limit`, `keepalive_timeout`）は適切ですが、ドキュメントの `Usage` 例が非推奨のスタンドアロン使用を促している点は改善が必要です。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
