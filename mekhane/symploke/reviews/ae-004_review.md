# 関数長の測量士 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` (117行): Critical (> 100行 - 禁止事項)
- `postcheck_boot_report` (115行): Critical (> 100行 - 禁止事項)
- `generate_boot_template` (104行): Critical (> 100行 - 禁止事項)
- `_load_projects` (61行): High (> 50行)
- `_load_skills` (57行): High (> 50行)
- `print_boot_summary` (41行): Medium (> 20行)
- `main` (30行): Medium (> 20行)

## 重大度
Critical
