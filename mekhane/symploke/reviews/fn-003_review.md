# 引数数の門番 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `with_retry` (Line 134): 5引数 (High)
- `JulesClient.__init__` (Line 196): 5引数 (High)
- `JulesClient.create_session` (Line 271): 6引数 (High)
- `JulesClient.poll_session` (Line 319): 5引数 (High)
- `JulesClient.create_and_poll` (Line 369): 5引数 (High)
- `JulesClient.synedrion_review` (Line 427): 6引数 (High)

## 重大度
High
