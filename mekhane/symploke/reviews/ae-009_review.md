# import順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- 標準ライブラリのimportがアルファベット順になっていない (`re`, `sys`, `json`, `argparse` の順序になっているが、`argparse`, `json`, `re`, `sys` であるべき) (Medium)

## 重大度
Medium
