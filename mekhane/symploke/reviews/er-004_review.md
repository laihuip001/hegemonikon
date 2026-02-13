# fail-fast伝道者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- create_session: prompt, source の入力検証が遅延している（空文字チェックなし） (High)
- batch_execute: tasks リスト内の各タスクに対するキー（prompt, source）の存在確認が遅延している（実行時にKeyErrorとなる） (High)
- poll_session: timeout, poll_interval の負値チェックがない (Medium)
- synedrion_review: フィルタリング（domains, axes）の結果が0件の場合に例外を投げず、空リストを返している（設定ミスに気づきにくい） (High)

## 重大度
High
