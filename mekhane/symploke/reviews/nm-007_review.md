# ブール命名の審判 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `gpu_ok` (L79, L300): ブール変数は `is_gpu_ok` または `can_use_gpu` 等の質問形にするべき (Medium)
- `all_checked` (L771): ブール変数は `are_all_checked` または `is_checklist_complete` 等の質問形にするべき (Medium)
- `wal_filled` (L785): ブール変数は `is_wal_filled` 等の質問形にするべき (Medium)
- `all_passed` (L836): ブール変数は `are_all_passed` または `is_passed` 等の質問形にするべき (Medium)

## 重大度
Medium
