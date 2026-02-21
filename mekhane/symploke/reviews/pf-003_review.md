# in list vs in set審判 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- _load_projects (145行目): ループ内でのタプル探索 `in ("kalon", "aristos", "autophonos")` (Medium)
- _load_projects (147行目): ループ内でのタプル探索 `in ("ccl", "kernel", "pepsis")` (Medium)
- _load_projects (149行目): ループ内でのタプル探索 `in ("hgk",)` (Medium)
- get_boot_context (347行目): リスト内包表記内のタプル探索 `in ("in_progress", "blocked")` (Medium)

## 重大度
Medium
