# ネスト深度警報者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` (Line 104): ネスト深度 6 (try -> for -> if -> for -> if -> if) - High
- `_load_skills` (Line 158): ネスト深度 6 (try -> for -> if -> if -> if -> try) - High
- `get_boot_context` (Line 207): ネスト深度 6 (if -> try -> if -> if -> if -> for) - High
- `print_boot_summary` (Line 319): ネスト深度 4 (try -> if -> for) - High

## 重大度
High
