# エラーハンドリング一貫性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **パターン混在 (Result Pattern vs Exception Pattern)**: `create_session` や `poll_session` は例外を送出する設計だが、`batch_execute` は `JulesResult` オブジェクトを返却してエラーを内部に保持する設計になっている。利用者はメソッドによってエラー処理の実装を変える必要がある。
- **抽象化の漏洩 (Leaky Abstraction)**: `_request` メソッドが `aiohttp` の例外 (`ClientResponseError` など) をそのまま送出している。`JulesError` 階層にラップされていないため、利用者は `aiohttp` の例外仕様を知る必要がある。
- **標準例外の不統一な使用**: タイムアウト時に `JulesError` のサブクラスではなく、標準の `TimeoutError` を使用している。
- **冗長な再試行ロジック**: `poll_session` 内で `RateLimitError` に対するバックオフ処理があるが、呼び出している `get_session` にも `with_retry` デコレータが適用されており、二重の再試行・待機構造になっている。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
