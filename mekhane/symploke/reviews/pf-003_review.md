# in list vs in set審判 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 関数内の `for p in projects:` ループにおいて、タプルへの所属判定 `in ("kalon", "aristos", "autophonos")`、`in ("ccl", "kernel", "pepsis")`、`in ("hgk",)` を行っているため、計算量がO(n)になっています。これらはset化してO(1)に最適化すべきです。 (Medium)
- `get_boot_context` 関数内の `[e for e in prev_wal.progress if e.status in ("in_progress", "blocked")]` (リスト内包表記) において、ループ内でタプルへの所属判定を行っているため、O(n)になっています。set化して最適化すべきです。 (Medium)

## 重大度
Medium
