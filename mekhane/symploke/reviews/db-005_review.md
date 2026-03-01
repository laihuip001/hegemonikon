# NOT NULL推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- [Medium] `get_boot_context` と `print_boot_summary` の引数 `context: Optional[str] = None` で不要な NULL を許可しており、関数内で `context or ""` のような NULL 判定が複雑化している。デフォルト値を `""` とすべきである。
- [Medium] `_load_projects` 内の `ep = p.get("entry_point")` で NULL を許容し、その後 `if ep and isinstance(ep, dict):` と判定が複雑化している。`p.get("entry_point", {})` とデフォルトの空辞書を渡すことで NULL 判定を排除できる。

## 重大度
Medium
