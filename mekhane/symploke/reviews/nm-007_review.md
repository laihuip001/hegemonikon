# ブール命名の審判 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- 変数 `gpu_ok` は `is_`/`has_`/`can_`/`should_` などの接頭辞がありません。 [Medium]
- 変数 `all_checked` は `is_`/`has_`/`can_`/`should_` などの接頭辞がありません。 [Medium]
- 変数 `wal_filled` は `is_`/`has_`/`can_`/`should_` などの接頭辞がありません。 [Medium]
- 変数 `all_passed` は `is_`/`has_`/`can_`/`should_` などの接頭辞がありません。 [Medium]

## 重大度
Medium