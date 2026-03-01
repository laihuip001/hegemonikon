# 空入力恐怖症 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `postcheck_boot_report`の`Check 1`において、入力`content`が空文字列の場合、`content.count("<!-- FILL -->")`が0になり「未記入セクションなし」として誤ってパスしてしまいます。(High)

## 重大度
High
