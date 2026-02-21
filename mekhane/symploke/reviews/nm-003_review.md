# 略語撲滅の十字軍 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- (L144) `cat_name`, `cat_projects`: `cat` は `category` に展開すべき (Medium)
- (L155) `ep`: `entry_point` の略語は不明瞭 (Medium)
- (L289) `gpu_pf`: `pf` (preflight) は一般的ではない (Medium)
- (L343) `wal_mgr`: `mgr` は明示的に禁止されている略語 (Medium)
- (L415) `req`: `request` と書くべき (Medium)
- (L456) `h_count`: `h` (handoff) は文脈依存が強い。`handoff_count` 推奨 (Medium)
- (L462-464) `proj_*`: `project_*` に展開すべき (Medium)
- (L465-467) `fb_*`: `feedback_*` に展開すべき (Medium)
- (L484, 582) `reqs`: `requirements` に展開すべき (Medium)
- (L661) `ci`: `ci` (check icon?) は意味不明瞭 (Medium)

## 重大度
Medium
