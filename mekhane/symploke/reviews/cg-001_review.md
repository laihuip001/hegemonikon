# ネスト深度警報者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`_load_projects`**:
  - `if len(summary) > 50:` (L164, Depth 4)
  - `if ep and isinstance(ep, dict):` (L169, Depth 4)
  - `if cli:` (L171, Depth 5)
  - `if trigger and p.get("status") == "active":` (L176, Depth 4)
- **`_load_skills`**:
  - `if len(parts) >= 3:` (L225, Depth 4)
  - `try:` (L227, Depth 5)
  - `if len(parts) >= 3:` (L239, Depth 4)
- **`get_boot_context`**:
  - `if prev_wal.blockers:` (L344, Depth 4)
  - `if incomplete:` (L348, Depth 4)
  - `for e in incomplete[:5]:` (L350, Depth 5)

## 重大度
High
