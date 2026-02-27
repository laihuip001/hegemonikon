# ネスト深度警報者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects`: ネスト深度 6 (Critical) - CLI情報の取得ロジックにて `try` > `for` > `if` > `if` > `if` の構造
- `_load_skills`: ネスト深度 6 (Critical) - YAMLフロントマター解析にて `try` > `for` > `if` > `if` > `try` の構造
- `get_boot_context`: ネスト深度 6 (Critical) - Intent-WALの未完了タスク表示にて `if` > `try` > `if` > `if` > `for` の構造
- `print_boot_summary`: ネスト深度 4 (High) - 今日の定理提案のループ処理にて `try` > `if` > `for` の構造

## 重大度
Critical
