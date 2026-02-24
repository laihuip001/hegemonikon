# ネスト深度警報者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects`: `if status == "archived":` 等の分岐 (Level 4)
- `_load_projects`: `if not cat_projects:` (Level 4)
- `_load_projects`: `for p in cat_projects:` (Level 4)
- `_load_projects`: `if len(summary) > 50:` (Level 5)
- `_load_projects`: `if ep and isinstance(ep, dict):` (Level 5)
- `_load_projects`: `if cli:` (Level 6)
- `_load_skills`: `if not skill_dir.is_dir()` (Level 4)
- `_load_skills`: `if content.startswith("---")` (Level 4)
- `_load_skills`: `if len(parts) >= 3:` (Level 5)
- `_load_skills`: `try:` ブロック (Level 6)
- `get_boot_context`: `if prev_wal:` (Level 4)
- `get_boot_context`: `if prev_wal.blockers:` (Level 5)
- `get_boot_context`: `if incomplete:` (Level 5)
- `get_boot_context`: `for e in incomplete[:5]:` (Level 6)
- `get_boot_context`: `if bc_entries:` (Level 4)
- `print_boot_summary`: `for t in suggestions:` (Level 4)

## 重大度
High
