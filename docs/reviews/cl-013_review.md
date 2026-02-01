# エラーハンドリング一貫性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **例外階層の混在:** カスタム例外 (`JulesError`)、ライブラリ例外 (`aiohttp.ClientError`)、標準例外 (`TimeoutError`, `ValueError`) が混在しており、呼び出し側で多岐にわたる例外捕捉が必要となっている。
- **エラー返却パターンの不一致:** 単体操作メソッド (`create_and_poll` 等) は例外を送出するが、バッチ操作メソッド (`batch_execute`) は例外を捕捉して `JulesResult` オブジェクト (Result パターン) を返す設計となっている。
- **エラー情報のデータ型不整合:** `JulesResult.error` は `Exception` オブジェクトを保持するが、`JulesSession.error` はエラーメッセージの `str` のみを保持しており、情報の粒度が異なる。
- **ネットワークエラーの扱い:** `create_and_poll` を直接呼ぶとネットワークエラー時に例外が発生するが、`batch_execute` 経由では `SessionState.FAILED` を持つセッションとして扱われ、挙動が一貫していない。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
