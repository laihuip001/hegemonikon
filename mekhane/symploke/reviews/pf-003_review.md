# in list vs in set審判 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`_load_projects` 内の `status` チェック (Medium)**:
  `projects` リスト (n) に対して、`active`, `dormant`, `archived` のリストをそれぞれ内包表記で生成しているため、O(3n) の走査が発生している。
  ```python
  active = [p for p in projects if p.get("status") == "active"]
  dormant = [p for p in projects if p.get("status") == "dormant"]
  archived = [p for p in projects if p.get("status") == "archived"]
  ```

- **`_load_projects` 内のカテゴリ振り分け (Medium)**:
  `projects` リスト (n) に対するループ内で、`p.get("id")` がタプル `("kalon", "aristos", "autophonos")` や `("ccl", "kernel", "pepsis")` に含まれるか (`in`) チェックしている。
  ```python
  elif path.startswith(".") or p.get("id") in ("kalon", "aristos", "autophonos"):
  elif p.get("id") in ("ccl", "kernel", "pepsis"):
  ```
  これらは定数タプルへの `in` なので Python では比較的高速だが、ID数が増えると O(m*n) になる可能性がある。Set 化 (`{"kalon", ...}`) が望ましい。

- **`get_boot_context` 内の `incomplete` タスク抽出 (Medium)**:
  `prev_wal.progress` リスト (n) に対して、`done` のカウントと `incomplete` リストの生成で2回走査している。
  ```python
  done = sum(1 for e in prev_wal.progress if e.status == "done")
  # ...
  incomplete = [e for e in prev_wal.progress if e.status in ("in_progress", "blocked")]
  ```
  `status` チェックの `("in_progress", "blocked")` はタプルへの `in` だが、ループ自体が複数回回っている。

## 重大度
Medium
