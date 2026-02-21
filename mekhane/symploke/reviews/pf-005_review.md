# generator推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `_load_projects` 関数内で `active`, `dormant`, `archived` をリスト内包表記で生成しているが、直後に `len()` で要素数しか使用していない。メモリ効率のためジェネレータ式と `sum()` を使用すべき (Low)
- `generate_boot_template` 関数内で `active`, `dormant`, `archived` をリスト内包表記で生成しているが、直後に `len()` で要素数しか使用していない (Low)
- `get_boot_context` 関数内で `incomplete` タスクをリスト内包表記で全件生成しているが、使用するのは先頭5件のみである。`itertools.islice` 等を用いたジェネレータ処理に変更可能 (Low)
- `postcheck_boot_report` 関数内で `re.findall` を用いてマッチ数をカウントしているが、リスト生成を伴うため `re.finditer` とジェネレータ式の組み合わせが望ましい (Low)

## 重大度
Low
