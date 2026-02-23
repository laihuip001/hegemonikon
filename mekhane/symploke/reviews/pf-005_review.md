# generator推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 関数内で `active`, `dormant`, `archived` のリストを `len()` のためだけに生成している (Low)
- `generate_boot_template` 関数内で `active`, `dormant`, `archived` のリストを `len()` のためだけに生成している (Low)
- `postcheck_boot_report` 関数内で `re.findall` を使用し、全マッチ結果のリストを `len()` のためだけに生成している (Low)

## 重大度
Low
