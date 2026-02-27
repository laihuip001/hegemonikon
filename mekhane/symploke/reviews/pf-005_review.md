# generator推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 関数にて、`active`, `dormant`, `archived` リストが `len()` 取得のためだけに生成されています。`sum(1 for ...)` ジェネレータ式への置き換えが推奨されます。(Low)
- `generate_boot_template` 関数にて、`active`, `dormant`, `archived` リストが `len()` 取得のためだけに生成されています。`sum(1 for ...)` ジェネレータ式への置き換えが推奨されます。(Low)

## 重大度
Low
