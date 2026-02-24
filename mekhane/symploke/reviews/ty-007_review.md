# 戻り値詐欺検出者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `print_boot_summary` 関数に型アノテーションがありません (High)
  - `-> None` が期待されます。プロジェクト規約で新規関数の型アノテーションは必須です。
- `main` 関数に型アノテーションがありません (High)
  - `-> None` または `-> NoReturn` が期待されます。

## 重大度
High
