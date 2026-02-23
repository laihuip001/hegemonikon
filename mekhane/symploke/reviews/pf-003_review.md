# in list vs in set審判 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 関数内で、ループごとに `in tuple` (O(n)) の探索が行われている。これらは定数セット (O(1)) として定義すべきである。
  - `p.get("id") in ("kalon", "aristos", "autophonos")`
  - `p.get("id") in ("ccl", "kernel", "pepsis")`
  - `p.get("id") in ("hgk",)`
- `get_boot_context` 関数内で、`in tuple` を用いたリスト内包表記が使用されている。これも set (O(1)) にすべきである。
  - `e.status in ("in_progress", "blocked")`

## 重大度
Medium
