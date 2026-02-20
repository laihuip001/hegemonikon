# generator推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 関数内において、`active`, `dormant`, `archived` のリスト生成が `len()` の計算のみを目的として行われています。これはメモリ効率が悪く、generator式（`sum(1 for ...)`）または単一ループでの集計に置き換えるべきです。(Low)
- `generate_boot_template` 関数内において、`active`, `dormant`, `archived` のリスト生成が統計表示（`len()`）のみを目的として行われています。リスト全体をメモリに展開する必要はなく、generator式を使用すべきです。(Low)

## 重大度
Low
