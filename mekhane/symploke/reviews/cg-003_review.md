# 三項演算子制限者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- ネストした三項演算子がL716-720で検出されました: `f"..." + (... if ... else ...) + ... if ... else ...` の形式です。

## 重大度
Medium
