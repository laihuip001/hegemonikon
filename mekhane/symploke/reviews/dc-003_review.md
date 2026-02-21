# 例示推進者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- [Low] `get_boot_context` 関数の docstring に Python API としての利用例 (Usage Example) が不足しています。CLI の usage は記載されていますが、ライブラリとして利用する場合（例: `>>> get_boot_context(mode="fast")`）のサンプルコードがありません。
- [Low] `mekhane/symploke/` またはプロジェクトルートに `examples/` ディレクトリが存在せず、統合やカスタマイズのためのサンプルコードが提供されていません。

## 重大度
Low
