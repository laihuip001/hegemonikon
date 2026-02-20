# ネスト深度警報者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects`: ネスト深度 7 (基準: 3) [High]
- `_load_skills`: ネスト深度 6 (基準: 3) [High]
- `get_boot_context`: ネスト深度 5 (基準: 3) [High]

## 重大度
High
