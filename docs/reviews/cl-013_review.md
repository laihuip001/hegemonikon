# エラーハンドリング一貫性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **例外階層の混合**: `RateLimitError` や `UnknownStateError` は `JulesError` を継承しているが、`poll_session` メソッドは標準の `TimeoutError` を送出し、`synedrion_review` は `ImportError` を送出している。すべてのエラーがドメイン固有の基底クラスに統合されていない。
- **エラーデータ型の不整合**: `JulesResult` クラスの `error` フィールドは `Exception` オブジェクトを保持するのに対し、`JulesSession` クラスの `error` フィールドは `str` (エラーメッセージ) を保持しており、データ構造間で型の一貫性がない。
- **エラー伝播パターンの非対称性**: 単一操作 (`create_session`, `get_session`) は例外を送出 (Raise) する設計だが、バッチ操作 (`batch_execute`) は例外を捕捉して Result オブジェクトに格納する設計となっており、呼び出し側のハンドリング戦略が統一されていない。
- **低レイヤー例外の漏洩**: `_request` メソッドにて `aiohttp.ClientResponseError` が `JulesError` にラップされずにそのまま送出される可能性があり、抽象化の漏れ (Leaky Abstraction) が存在している。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
