# in list vs in set審判 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- _load_projects 関数内のループで `p.get("id") in ("kalon", "aristos", "autophonos")` が使用されている。set定数化すべき。(Medium)
- _load_projects 関数内のループで `p.get("id") in ("ccl", "kernel", "pepsis")` が使用されている。set定数化すべき。(Medium)
- _load_projects 関数内のループで `p.get("id") in ("hgk",)` が使用されている。set定数化すべき。(Medium)
- get_boot_context 関数内のリスト内包表記で `e.status in ("in_progress", "blocked")` が使用されている。set定数化すべき。(Medium)

## 重大度
Medium
