# 関数長の嘆き手 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` (62行): 50行超過 (High)
- `_load_skills` (56行): 50行超過 (High)
- `get_boot_context` (109行): 100行超過 (High - プロジェクト禁止事項抵触)
- `print_boot_summary` (34行): 20行超過 (Medium)
- `generate_boot_template` (102行): 100行超過 (High - プロジェクト禁止事項抵触)
- `postcheck_boot_report` (124行): 100行超過 (High - プロジェクト禁止事項抵触)
- `main` (27行): 20行超過 (Medium)

## 重大度
High
