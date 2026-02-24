# メソッド順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- パブリック関数 `get_boot_context` が、プロテクテッド関数 `_load_projects`, `_load_skills` よりも後に定義されています。
- パブリック関数 `print_boot_summary` が、プロテクテッド関数よりも後に定義されています。
- パブリック関数 `generate_boot_template` が、プロテクテッド関数よりも後に定義されています。
- パブリック関数 `postcheck_boot_report` が、プロテクテッド関数よりも後に定義されています。

## 重大度
Low
