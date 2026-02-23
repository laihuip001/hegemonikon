# 略語撲滅の十字軍 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **mgr** (Medium): `wal_mgr` (330行目) は `wal_manager` に展開すべき。読者への配慮が不足している。
- **cat** (137行目): `cat_name`, `cat_projects` は `category_name`, `category_projects` に展開すべき。
- **ep** (152行目): `ep` は `entry_point` に展開すべき。文脈なしでは意味が不明瞭。
- **pf** (301行目): `_gpu_pf` は `_gpu_preflight` に展開すべき。
- **req**, **reqs** (424, 499行目): `req`, `reqs` は `request`, `requirements` に展開すべき。
- **h** (527行目): `for i, h in ...` の `h` は `handoff` に展開すべき。単一文字変数は避ける。
- **proj** (468-470行目): `proj_total`, `proj_active` 等は `project_...` に展開すべき。
- **fb** (471-473行目): `fb_total`, `fb_rate` 等は `feedback_...` に展開すべき。
- **ci** (625行目): `ci` は `check_icon` 等に展開すべき。文脈的に icon を意味するが略語が強すぎる。

## 重大度
Medium
