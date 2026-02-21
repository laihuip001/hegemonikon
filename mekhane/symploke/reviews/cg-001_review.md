# ネスト深度警報者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- High: `_load_projects` 内の `entry_point` 処理 (L132-136) がネスト深度6に達している
- High: `_load_projects` 内の `usage_trigger` 処理 (L138-140) がネスト深度5に達している
- High: `_load_skills` 内の YAML frontmatter パース処理 (L177-182) がネスト深度6に達している
- High: `get_boot_context` 内の `Intent-WAL` 未完了タスク処理 (L274-291) がネスト深度6に達している

## 重大度
High
