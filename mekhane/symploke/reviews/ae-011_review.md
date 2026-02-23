# docstring構造家 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- main: docstring欠如 (Medium)
- get_boot_context: 一行目が動詞でない, ピリオド欠落 (Low)
- generate_boot_template: 一行目が動詞でない, Args/Returns不足 (Low)
- postcheck_boot_report: 一行目が動詞でない, Args不足 (Low)
- extract_dispatch_info: Args/Returns不足 (Low)
- print_boot_summary: Args不足 (Low)

## 重大度
Medium
