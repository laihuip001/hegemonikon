# 略語撲滅の十字軍 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **`wal_mgr` (340行目)**: `wal_manager` にすべき。
- **`_gpu_pf` (282行目)**: `gpu_preflight` という明確な名前があるのに `as _gpu_pf` としてインポートしている。
- **`reqs` (582行目など)**: `requirements` にすべき。
- **`req` (441行目)**: `request` にすべき。
- **`ep` (167行目)**: `entry_point` にすべき。
- **`cat_name`, `cat_projects` (155行目)**: `category_name`, `category_projects` にすべき。
- **`fmt` (381行目)**: `formatted_output` または `formatted_text` にすべき。

## 重大度
Medium
