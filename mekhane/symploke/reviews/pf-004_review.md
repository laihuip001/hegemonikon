# 再計算防止者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` (L129-142): `projects` リストに対して status 別のフィルタリングで3回、その後のカテゴリ分けループで1回、計4回の反復が行われている。1回のループ内でカウントと分類を行うべき。
- `_load_skills` (L226, L236): `content.split("---", 2)` が同一条件下で2回実行されている。結果を変数にキャッシュして再利用すべき。
- `generate_boot_template` (L438-442): `_load_projects` と同様に、`projects` リストに対して不要な複数回の反復（フィルタリング3回 + ループ1回）が行われている。
- `postcheck_boot_report` (L514, L566): `content.count("<!-- FILL -->")` が `fill_count` と `fill_remaining` の計算で2回実行されている。最初の計算結果を再利用すべき。

## 重大度
Low
