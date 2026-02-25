# メソッド順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Public関数 `get_boot_context` が Protected関数 `_load_projects`, `_load_skills` の後に配置されている (Low)
- Public関数 `print_boot_summary` が Protected関数 `_load_projects`, `_load_skills` の後に配置されている (Low)
- Public関数 `generate_boot_template` が Protected関数 `_load_projects`, `_load_skills` の後に配置されている (Low)
- Public関数 `postcheck_boot_report` が Protected関数 `_load_projects`, `_load_skills` の後に配置されている (Low)

## 重大度
Low
