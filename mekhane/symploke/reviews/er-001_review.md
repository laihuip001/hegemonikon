# 例外メッセージの詩人 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- **Line 41, 239 (`RateLimitError`)**: メッセージ "Rate limit exceeded" はエラーの原因のみを述べており、読者に対する次の行動（例：「しばらく待ってから再試行してください」）が示されていません。(Medium)
- **Line 52 (`UnknownStateError`)**: メッセージ "Unknown session state '{state}'..." は状態が不明であることを示していますが、対処法（例：「クライアントライブラリを更新してください」や「ログを確認してください」）が含まれていません。(Medium)
- **Line 383 (`TimeoutError`)**: メッセージ "Session ... did not complete within ...s" はタイムアウトの事実のみを伝えており、対処法（例：「タイムアウト時間を延ばすか、システムの状態を確認してください」）が欠けています。(Medium)

## 重大度
Medium
