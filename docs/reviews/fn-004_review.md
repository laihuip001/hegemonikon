# early return推進者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `poll_session` メソッド内のUNKNOWN状態処理が深いネスト（4段: while -> try -> if -> if）になっています。Medium
- `with_retry` デコレータ内の例外処理ロジックが深いネスト（4段: for -> try -> except -> if）になっています。Medium
- `main` 関数全体が `if args.test:` ブロックで囲まれており、guard clause (`if not args.test: return`) を使うことでネストを浅くできます。Medium

## 重大度
Medium
