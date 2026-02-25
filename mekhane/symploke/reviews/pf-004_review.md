# 再計算防止者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`_load_skills` における `split` の重複**: `content.split("---", 2)` が2回呼び出されています（YAML frontmatter 判定時と body 抽出時）。一度変数に格納して再利用すべきです。(Low)
- **`postcheck_boot_report` における `count` の重複**: `content.count("<!-- FILL -->")` が2回呼び出されています（`fill_count` と `fill_remaining`）。`fill_count` を再利用できます。(Low)
- **`_load_projects` および `generate_boot_template` におけるリスト内包表記の重複**: `active`, `dormant`, `archived` を算出するために `projects` リストを3回走査しています。1回のループで集計するか、メインのループ内でカウント可能です。(Low)
- **`_load_projects` および `generate_boot_template` における辞書アクセスの重複**: ループ内で `p.get("status")` が複数回呼び出されています。変数 `status` を一貫して使用すべきです。(Low)

## 重大度
Low
