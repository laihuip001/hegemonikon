# 再計算防止者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 関数内で `projects` リストを4回反復している（`active`/`dormant`/`archived` のリスト内包表記3回 + カテゴリ分けループ1回）。1回のループで集計と分類が可能である。
- `_load_projects` のカテゴリ分けループ内で `p.get("id")` が複数回呼び出されている（変数に格納すべき）。
- `_load_skills` 関数内で `content.split("---", 2)` が2回実行されている（変数に格納すべき）。
- `generate_boot_template` 関数内で `active`/`dormant`/`archived` リストを再生成して `len()` を取得しているが、これは `result["projects"]` に既にある値 (`active`, `dormant` キー) を利用できる。
- `postcheck_boot_report` 関数内で `content.count("<!-- FILL -->")` が2回実行されている（変数に格納すべき）。

## 重大度
Low
