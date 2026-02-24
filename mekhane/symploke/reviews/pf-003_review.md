# in list vs in set審判 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 内のループで `p.get("id") in ("kalon", "aristos", "autophonos")` (O(n) tuple lookup)
- `_load_projects` 内のループで `p.get("id") in ("ccl", "kernel", "pepsis")` (O(n) tuple lookup)
- `_load_projects` 内のループで `p.get("id") in ("hgk",)` (O(n) tuple lookup)
- `get_boot_context` 内の `incomplete` リスト内包表記で `e.status in ("in_progress", "blocked")` (O(n) tuple lookup)

## 重大度
Medium
