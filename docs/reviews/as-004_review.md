# 非同期リソース管理評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **非効率なセッション管理**: `JulesClient` は `async with` コンテキストマネージャをサポートしていますが、docstring の使用例 (`client = JulesClient(...)`) ではコンテキストマネージャを使用していません。
- **リソースの無駄遣い**: コンテキストマネージャを使用しない場合、`_request` メソッドが呼び出されるたびに新しい `aiohttp.ClientSession` が作成され、即座に破棄されます（`close_after=True`）。これにより、以下の問題が発生します：
    - コネクションプーリング（Keep-Alive）が無効化され、TCPハンドシェイクのオーバーヘッドが増大する。
    - `batch_execute` や `poll_session` のような頻繁なAPI呼び出しを行う操作において、短時間に大量のソケットを開閉することになり、ポート枯渇のリスクがある。
    - `__init__` で `self._owned_session` を初期化せず、`__aenter__` でのみ初期化する設計になっているため、明示的に `async with` を使用しない限り、この非効率な動作が強制される。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
