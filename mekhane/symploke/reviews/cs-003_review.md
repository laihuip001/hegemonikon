# メソッド順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- Protected関数 `_load_projects` が Public関数 `get_boot_context` よりも先に定義されています (Low)
- Protected関数 `_load_skills` が Public関数 `get_boot_context` よりも先に定義されています (Low)

## 重大度
Low
