# in list vs in set審判 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 関数内のループで、`p.get("id")` の判定にタプル `(...)` が使用されている（`("kalon", "aristos", "autophonos")`, `("ccl", "kernel", "pepsis")`）。ループ内で繰り返し実行されるため、セット `in {...}` または定数セットを使用すべき。
- `get_boot_context` 内の `IntentWAL` 処理において、`e.status in ("in_progress", "blocked")` というタプルへの `in` 演算が行われている。

## 重大度
Medium
