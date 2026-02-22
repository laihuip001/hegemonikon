# 略語撲滅の十字軍 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **mgr** (L227): `wal_mgr` (IntentWALManager) - 明示的に禁止された略語 (`manager` と書くべき)
- **cat** (L119): `cat_name`, `cat_projects` - Unixコマンドの `cat` (concatenate) と紛らわしい (`category` と書くべき)
- **ep** (L126): `ep` - `entry_point` の極端な省略
- **pf** (L196): `_gpu_pf` - `preflight` の略語としては一般的ではない
- **req** (L310): `req` - `request` の略語 (明示的に禁止された略語リストに含まれる)
- **h** (L333, L383): `h_count`, `h` - `handoff` の略語 (文脈依存度が高い)
- **proj** (L341): `proj_total`, `proj_active` - `project` の中途半端な省略
- **fb** (L344): `fb_total`, `fb_rate` - `feedback` の略語
- **ci** (L550): `ci` - `check_icon` または `status_icon` の意図と思われるが不明瞭

## 重大度
Medium
