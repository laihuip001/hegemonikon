# 過保護try検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `main` 関数 (L771-782): `try-except Exception` ブロックが、クライアント初期化時の全ての例外を捕捉し、エラーメッセージのみを表示して終了 (`exit(1)`) しています。これによりスタックトレースが隠蔽され、デバッグが困難になります。(Critical)
- `batch_execute` 内の `bounded_execute` 関数 (L575-598): `try-except Exception` ブロックで例外を捕捉し、`JulesResult` にラップしていますが、`logger.error` でログ出力する際に `exc_info=True` がないため、ログ上でスタックトレースが失われます。(Medium)

## 重大度
High
