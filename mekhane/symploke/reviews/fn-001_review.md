# 関数長の嘆き手 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` (110行): High - 50行超過（絶望）
- `postcheck_boot_report` (101行): High - 50行超過（絶望）
- `generate_boot_template` (90行): High - 50行超過（絶望）
- `_load_projects` (61行): High - 50行超過（絶望）
- `_load_skills` (53行): High - 50行超過（絶望）
- `print_boot_summary` (36行): Medium - 20行超過（泣く）
- `main` (28行): Medium - 20行超過（泣く）

## 重大度
High
