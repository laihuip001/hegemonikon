<!-- PROOF: [L2/Review] <- mekhane/symploke/boot_integration.py -->
# None恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **High**: `_load_projects` 関数内で `yaml.safe_load` の戻り値が `None` になるケース（空ファイル等）が考慮されていません。`data` が `None` の場合、直後の `data.get("projects", [])` で `AttributeError` が発生します。
- **High**: `_load_skills` 関数内で `yaml.safe_load` の戻り値が `None` になるケース（空のFrontmatter等）が考慮されていません。`meta` が `None` の場合、直後の `meta.get("name", ...)` で `AttributeError` が発生します。
- **Medium**: `extract_dispatch_info` 関数の引数 `context` は `str` 型として定義されていますが、`None` チェックがありません。呼び出し元によっては `None` が渡る可能性があり（`get_boot_context` では `Optional[str]`）、その場合 `dispatcher.dispatch(context)` で予期せぬエラーが発生するリスクがあります。

## 重大度
High
