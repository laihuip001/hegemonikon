# tryブロック最小化者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` (118-176行): 59行の巨大なtryブロック。YAMLパース、データ加工、整形ロジックが混在しており、誤った例外捕捉のリスクがある (Medium)
- `_load_skills` (189-245行): 57行の巨大なtryブロック。ファイル操作、ループ、整形が混在している (Medium)
- `_load_skills` (203行): tryブロック内部にネストされたtryブロックが存在する (Medium)
- `get_boot_context` (287-313行): WAL読み込み処理全体（27行）が単一のtryブロックに含まれている (Medium)
- `get_boot_context` (367-382行): n8n通知処理（16行）がJSON生成からHTTP通信まで単一のtryブロックに含まれている (Medium)
- `print_boot_summary` (394-408行): 定理提案機能（15行）が単一のtryブロックに含まれている (Medium)
- `get_boot_context` (342-353行): BC違反ログ読み込み処理（12行）が単一のtryブロックに含まれている (Medium)
- `extract_dispatch_info` (90-100行): 11行のtryブロック。インポート、実行、整形が混在している (Medium)

## 重大度
Medium
