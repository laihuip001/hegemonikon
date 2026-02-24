# ブール命名の審判 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- extract_dispatch_info 関数の引数 `gpu_ok` (行 74) に is_/has_/can_/should_ 接頭辞がありません (Medium)
- get_boot_context 関数の変数 `gpu_ok` (行 239) に is_/has_/can_/should_ 接頭辞がありません (Medium)
- postcheck_boot_report 関数の変数 `all_checked` (行 534) に is_/has_/can_/should_ 接頭辞がありません (Medium)
- postcheck_boot_report 関数の変数 `wal_filled` (行 545) に is_/has_/can_/should_ 接頭辞がありません (Medium)
- postcheck_boot_report 関数の変数 `all_passed` (行 587) に is_/has_/can_/should_ 接頭辞がありません (Medium)

## 重大度
Medium
