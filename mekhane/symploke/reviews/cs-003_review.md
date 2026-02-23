# メソッド順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Publicメソッド (`get_boot_context`, `print_boot_summary`, `generate_boot_template`, `postcheck_boot_report`, `main`) が Protectedメソッド (`_load_projects`, `_load_skills`) の後に配置されています (Low)

## 重大度
Low
