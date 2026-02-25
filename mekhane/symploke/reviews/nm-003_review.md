# 略語撲滅の十字軍 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `wal_mgr` (Line 335): `mgr` は読者への配慮に欠ける (Medium)
- `_gpu_pf` (Line 292): `pf` は不明瞭 (preflight?) (Medium)
- `reqs` (Line 582): `reqs` は不明瞭 (requirements?) (Medium)
- `req` (Line 436): `req` は文脈依存 (request?) (Medium)
- `ep` (Line 168): `ep` は不明瞭 (entry_point?) (Medium)
- `cat_name`, `cat_projects` (Line 155): `cat` は不明瞭 (category?) (Medium)
- `fmt` (Line 391): `fmt` は不適切な省略 (formatted?) (Medium)
- `proj_*` (Line 507): `proj` は不適切な省略 (project?) (Medium)
- `fb_*` (Line 510): `fb` は不明瞭 (feedback?) (Medium)
- `ci` (Line 843): `ci` は不明瞭 (check_icon/item?) (Medium)

## 重大度
Medium
