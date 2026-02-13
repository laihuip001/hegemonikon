# early return推進者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `poll_session` メソッド内の `while` ループにおいて、 `try` -> `if session.state == SessionState.UNKNOWN` -> `if consecutive_unknown >= 3` とネストが4段に達しており、可読性を低下させています。(Medium)
- `with_retry` デコレータ内の `except` ブロックにおいて、`if attempt == max_attempts - 1` や `if isinstance(...)` による条件分岐があり、ネストが3段に達しています。(Medium)
- `main` 関数において、処理全体が `if args.test:` のブロック内に記述されています。ガード節 (`if not args.test: return`) を導入することで、主要なロジックのインデントを下げることができます。(Low)

## 重大度
Medium
