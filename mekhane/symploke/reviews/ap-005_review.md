# Content-Type警察 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `self._headers` に `Content-Type: application/json` がハードコードされており、GETリクエストなど本来ボディを持たないリクエストでも送信されています（嘘のContent-Type）。
- `_request` メソッドで `json` パラメータを使用しているため、`aiohttp` が自動的に適切なヘッダーを設定します。手動での設定は不要であり、有害です。

## 重大度
High
