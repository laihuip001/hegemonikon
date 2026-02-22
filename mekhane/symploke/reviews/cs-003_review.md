# メソッド順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- protected メソッド `_load_projects`, `_load_skills` が public メソッド `get_boot_context` 以降のメソッドよりも先に定義されており、public → protected → private の順序に違反している (Low)

## 重大度
Low
