# Content-Type警察 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `JulesClient.__init__` 内で `self._headers` に `Content-Type: application/json` がハードコードされており、GETリクエスト（bodyなし）を含む全てのリクエストで送信されている。これは「JSONならapplication/json、嘘をつくな」の原則に違反する（Content-Type嘘: High）。
- `_request` メソッドでは `aiohttp` の `json` パラメータを使用しており、`aiohttp` が自動的に適切な `Content-Type` ヘッダーを設定するため、手動でのヘッダー指定は冗長かつ不適切である。

## 重大度
High
