# import順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- 標準ライブラリのimport順序がアルファベット順になっていません (`re`, `sys`, `json`, `argparse` の順になっていますが、`argparse` は先頭に来るべきです) (Medium)
- 関数内のローカルimportがアルファベット順にソートされていません (Medium)

## 重大度
Medium
