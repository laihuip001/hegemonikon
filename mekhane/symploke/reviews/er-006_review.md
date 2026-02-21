# tryブロック最小化者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **巨大try (Medium)**: `_load_projects` 内の try ブロックが約 60 行に及び、インポート、ファイル読み込み、YAML解析、データ整形ロジックを全て囲んでいます。
- **巨大try (Medium)**: `_load_skills` 内の try ブロックが約 45 行に及び、ディレクトリ走査とファイル処理全体を囲んでいます。
- **tryの中にtry (Medium)**: `_load_skills` 内のループ中で YAML パースのためにネストされた try ブロックが存在します。
- **巨大try (Medium)**: `get_boot_context` 内の Intent-WAL 読み込み処理 (約 19 行)、n8n 通知処理 (約 12 行)、BC違反チェック (約 11 行) がそれぞれ広い範囲を try で囲んでいます。
- **巨大try (Medium)**: `print_boot_summary` 内の「今日の定理提案」処理 (約 11 行) が広い範囲を try で囲んでいます。

## 重大度
Medium
