# 関数長の測量士 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` (70行): High - 50行超過
- `_load_skills` (63行): High - 50行超過
- `get_boot_context` (112行): High - 50行超過 (100行超は禁止事項に該当)
- `print_boot_summary` (41行): Medium - 20行超過
- `generate_boot_template` (106行): High - 50行超過 (100行超は禁止事項に該当)
- `postcheck_boot_report` (123行): High - 50行超過 (100行超は禁止事項に該当)
- `main` (34行): Medium - 20行超過

## 重大度
High
