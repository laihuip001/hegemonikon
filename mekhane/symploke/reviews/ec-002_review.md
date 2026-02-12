# None恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `get_session` メソッドにて、APIレスポンスの `pullRequest` が `null` の場合、`pr.get("url")` でクラッシュする可能性があります (High)。
- `get_session` メソッドにて、APIレスポンスの `sourceContext` が `null` の場合、`data.get("sourceContext", {}).get("source", "")` でクラッシュする可能性があります (High)。
- `create_session` メソッドにて、APIレスポンスの `id`, `name` が欠損または `null` の場合を考慮していません (Medium)。

## 重大度
High
