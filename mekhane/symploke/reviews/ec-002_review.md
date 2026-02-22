# None恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` 内で `handoffs_result["latest"].metadata` にアクセスする際、`latest` オブジェクトが `metadata` 属性を持つか、またそれが `None` でないかのチェックがありません (High)
- `generate_boot_template` 内で `h.metadata.get(...)` および `ki.metadata.get(...)` を呼び出す際、`hasattr` チェックのみで `None` チェックがありません。`metadata` が `None` の場合 `AttributeError` になります (High)
- `extract_dispatch_info` の `context` 引数は `str` 型ヒントですが、`None` チェックがなく、`AttractorDispatcher` にそのまま渡されるとクラッシュする可能性があります (Medium)

## 重大度
High
