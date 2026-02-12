# 関数長の嘆き手 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `with_retry`: 54行 (High)
- `JulesClient.__init__`: 36行 (Medium)
- `JulesClient._request`: 54行 (High)
- `JulesClient.create_session`: 39行 (Medium)
- `JulesClient.get_session`: 33行 (Medium)
- `JulesClient.poll_session`: 61行 (High)
- `JulesClient.batch_execute`: 72行 (High)
- `JulesClient.synedrion_review`: 98行 (High)
- `main`: 28行 (Medium)

## 重大度
High
