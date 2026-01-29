# リソースリーク検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `JulesClient` をコンテキストマネージャ（`async with`）として使用しない場合、`_request` メソッドが呼び出されるたびに新しい `aiohttp.ClientSession` が作成され、即座に閉じられる実装になっている。
- 特に `poll_session` メソッドは内部ループで `get_session` を繰り返し呼び出すため、短期間に多数の `ClientSession` の作成と破棄が発生する。
- これにより、OS レベルで TIME_WAIT 状態の TCP ソケットが大量に発生し、ポート枯渇（Ephemeral Port Exhaustion）を引き起こすリスクがある。これは未解放リソースの一種（システムリソースの浪費）とみなされる。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
