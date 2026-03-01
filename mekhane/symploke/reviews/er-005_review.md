# raise再投げ監視官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- 例外を握りつぶしてログだけ (High): Line 410 `except Exception as e:` blocks missing `raise` or missing `exc_info=True`.
- 例外を握りつぶしてログだけ (High): Line 889 `except Exception as e:` blocks missing `raise` or missing `exc_info=True`.

## 重大度
High
