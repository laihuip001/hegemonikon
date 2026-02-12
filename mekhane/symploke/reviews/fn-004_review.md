# early return推進者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- poll_session メソッド内の while ループにおいて、try-except ブロックの中に if 文がネストしており、さらにその中に if 文が存在するため、ネストが4段に達しています。 (Medium)
- with_retry デコレータ内の wrapper 関数において、for ループ、try-except、さらにその中に if 文があり、ネストが深くなっています。 (Medium)
- _request メソッドにおいて、try ブロック、async with ブロック、その中の if 文により、ネストが3段になっています。 (Medium)
- main 関数において、処理の大部分が `if args.test:` ブロック内に記述されています。early return を用いることでネストを削減できます。 (Low)

## 重大度
Medium
