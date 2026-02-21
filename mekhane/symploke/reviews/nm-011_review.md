# private接頭辞の監視者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` が private (`_`) 接頭辞を持つが、`mekhane/symploke/boot_axes.py` から参照されている。これは内部実装の隠蔽契約に違反している。(Medium)
- `_load_skills` が private (`_`) 接頭辞を持つが、`mekhane/symploke/boot_axes.py` から参照されている。これは内部実装の隠蔽契約に違反している。(Medium)
- `generate_boot_template` が public 接頭辞を持つが、`print_boot_summary` からのみ参照される内部ヘルパーであり、外部モジュールからの利用がないため、`_generate_boot_template` とすべきである。(Medium)

## 重大度
Medium
