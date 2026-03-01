# 定数命名の番人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- ローカル変数 `status_icons` が複数箇所（`_load_projects`, `generate_boot_template` 関数内）で定義されており、実質的に定数として扱われています。SCREAMING_SNAKE_CASEのモジュールレベル定数（例: `STATUS_ICONS`）として抽出してください。

## 重大度
Medium