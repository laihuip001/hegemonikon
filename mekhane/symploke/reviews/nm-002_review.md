# 動詞/名詞の裁定者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- [Medium] 関数名 `_gpu_pf` (エイリアス) は名詞句 `GPU Preflight` の省略形です。動詞で始めるべきです (例: `_check_gpu`)。
- [Medium] 関数名 `todays_theorem` (インポート) は名詞句です。動詞で始めるべきです (例: `suggest_todays_theorem`)。
- [Medium] 関数名 `usage_summary` (インポート) は名詞句です。動詞で始めるべきです (例: `get_usage_summary`)。
- [Medium] 変数名 `active` (リスト) は形容詞です。名詞にするべきです (例: `active_projects`)。
- [Medium] 変数名 `dormant` (リスト) は形容詞です。名詞にするべきです (例: `dormant_projects`)。
- [Medium] 変数名 `archived` (リスト) は形容詞です。名詞にするべきです (例: `archived_projects`)。
- [Medium] 変数名 `incomplete` (リスト) は形容詞です。名詞にするべきです (例: `incomplete_tasks`)。
- [Medium] 変数名 `related` (リスト) は形容詞です。名詞にするべきです (例: `related_handoffs`)。
- [Medium] 変数名 `unchecked` (整数) は形容詞です。名詞にするべきです (例: `unchecked_count`)。
- [Medium] 変数名 `checked` (整数) は形容詞です。名詞にするべきです (例: `checked_count`)。

## 重大度
Medium
