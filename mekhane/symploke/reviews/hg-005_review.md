# 定理整合性監査官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **Design Principle Violation (Reduced Complexity)**: `get_boot_context` (114 lines) and `generate_boot_template` (110 lines) exceed the 100-line limit for single functions.
- **Project Convention Violation (Missing PURPOSE)**: Function `_load_projects` lacks a `# PURPOSE:` comment.
- **Project Convention Violation (Comment Language)**: Extensive use of Japanese in inline comments (e.g., `# 環境強制: ...`, `# 表示順: ...`) and some `# PURPOSE:` comments. Code comments must be in English.
- **Consistency Violation**: Mixed language in `# PURPOSE:` comments (some English, some Japanese).

## 重大度
Medium
