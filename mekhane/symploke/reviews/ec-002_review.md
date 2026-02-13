# None恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `get_session` メソッド内: `pullRequest` フィールドが `null` の場合、`pr` 変数が `None` となり、直後の `pr.get("url")` で `AttributeError` が発生します。(High)
- `get_session` メソッド内: `sourceContext` フィールドが `null` の場合、`data.get("sourceContext", {})` が `None` を返し、直後の `.get("source", "")` で `AttributeError` が発生します。(High)

## 重大度
High
