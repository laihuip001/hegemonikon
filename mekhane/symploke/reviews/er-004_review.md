# fail-fast伝道者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- create_session: prompt, source が空文字列でないか検証していない (High)
- get_session / poll_session: session_id が空文字列でないか検証していない (High)
- batch_execute: tasks リストの要素が辞書であり、必要なキーを持つかどうかの検証をループ実行前に行っていない (High)
- batch_execute: 一般的な Exception を捕捉しており、KeyError などのバグを隠蔽する可能性がある (Medium)

## 重大度
High
