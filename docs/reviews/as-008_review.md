# コネクションプール評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `_session` プロパティの実装に問題があります。`self._shared_session` や `self._owned_session` が存在しない場合、アクセスごとに新しい `aiohttp.ClientSession()` をインスタンス化して返していますが、これは変数に保持されません。内部的には使用されていませんが、外部からこのプロパティにアクセスした場合、セッションがクローズされずリソースリーク（Unclosed client session）を引き起こすリスクが高い「罠」となっています。
- クラスのDocstringにある使用例（Usage）が、コンテキストマネージャ（`async with`）を使用しない方法を推奨しています。コンテキストマネージャを使用しない場合、`_request` メソッドはリクエストごとに新しいセッションを作成・破棄します。これはコネクションプール（`TCPConnector`）の恩恵を無効化し、特にポーリング（`poll_session`）やバッチ処理においてTCP/SSLハンドシェイクのオーバーヘッドを増大させます。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
