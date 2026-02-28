# ジェネリクスの調律師 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `THEOREM_REGISTRY` で要素型が指定されていない生の `dict` が使われている。 (`dict[str, dict]`)
- `extract_dispatch_info` の戻り値の型で要素型が指定されていない生の `dict` が使われている。
- `_load_projects` の戻り値の型で要素型が指定されていない生の `dict` が使われている。
- `_load_skills` の戻り値の型で要素型が指定されていない生の `dict` が使われている。
- `get_boot_context` の戻り値の型で要素型が指定されていない生の `dict` が使われている。
- `generate_boot_template` の引数 `result` の型で要素型が指定されていない生の `dict` が使われている。
- `postcheck_boot_report` の戻り値の型で要素型が指定されていない生の `dict` が使われている。

## 重大度
Medium