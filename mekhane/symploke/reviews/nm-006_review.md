# getの追放者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context`: 関数名に `get` が使用されています。この関数は複数の軸（Axes）から情報をロード・統合する処理を行っているため、`assemble_boot_context`、`collect_boot_context`、あるいは `retrieve_boot_context` など、より具体的な動詞の使用が推奨されます。(Low)

## 重大度
Low
