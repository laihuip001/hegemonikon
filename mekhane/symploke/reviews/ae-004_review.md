# 関数長の測量士 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- JulesClient.synedrion_review (95行): high
- JulesClient.batch_execute (74行): high
- JulesClient.poll_session (59行): high
- JulesClient._request (53行): high
- with_retry (53行): high
- JulesClient.create_session (31行): medium
- JulesClient.get_session (27行): medium
- JulesClient.__init__ (25行): medium
- main (25行): medium

## 重大度
High
