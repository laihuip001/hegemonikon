# 再計算防止者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- _load_skills 内で `content.split("---", 2)` が2回実行されている (Low)
- _load_projects 内で `projects` リストを4回反復している (3回のリスト内包表記 + 1回のループ) (Low)
- generate_boot_template 内で `projects` から `active`/`dormant` を再計算している (呼び出し元ですでに計算済み) (Low)
- postcheck_boot_report 内で `checks` リストを2回反復している (`sum` と `all`) (Low)

## 重大度
Low
