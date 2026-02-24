# raise再投げ監視官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` (L410): 例外を捕捉してログ出力のみを行い、再送出していない (logging.debug)。因果が途切れている。 (Low)

## 重大度
Low
