# ネスト深度警報者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 関数: `try:` -> `for cat_name, cat_projects in categories.items():` -> `for p in cat_projects:` -> `if ep and isinstance(ep, dict):` -> `if cli:` で5段のネスト
- `_load_skills` 関数: `try:` -> `for skill_dir in sorted(skills_dir.iterdir()):` -> `if content.startswith("---"):` -> `if len(parts) >= 3:` -> `try:` で5段のネスト
- `get_boot_context` 関数: `if mode != "fast":` -> `try:` -> `if prev_wal:` -> `if incomplete:` -> `for e in incomplete[:5]:` で5段のネスト

## 重大度
High
