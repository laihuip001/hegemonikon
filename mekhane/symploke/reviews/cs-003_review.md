# メソッド順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `JulesClient` クラスにおいて、protected メソッド (`_session`, `_request`) が public メソッド (`create_session` 等) よりも先に定義されています。(Low)

## 重大度
Low
