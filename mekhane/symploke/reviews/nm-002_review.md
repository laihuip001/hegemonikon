# 動詞/名詞の裁定者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- SessionState.from_string: 関数名が前置詞 `from` で始まっています。`parse_string` や `create_from_string` 等の動詞で始めるべきです。(Medium)
- with_retry: 関数名が前置詞 `with` で始まっています。`apply_retry` 等の動詞で始めるべきです。(Medium)
- with_retry.decorator: 内部関数名が名詞 `decorator` です。`create_decorator` 等の動詞にするべきです。(Medium)
- with_retry.decorator.wrapper: 内部関数名が名詞 `wrapper` です。`execute_with_retry` や `wrap_function` 等の動詞にするべきです。(Medium)
- JulesClient._request: `request` は名詞としても解釈され曖昧です。`send_request` や `perform_request` 等の明示的な動詞が望ましいです。(Low)
- JulesClient.batch_execute: `batch` (名詞的) で始まっています。`execute_batch` (動詞+目的語) の語順が適切です。(Medium)
- JulesClient.batch_execute.bounded_execute: 形容詞 `bounded` で始まっています。`execute_bounded` とすべきです。(Medium)
- JulesClient.batch_execute.tracked_execute: 形容詞 `tracked` で始まっています。`execute_tracked` とすべきです。(Medium)
- JulesClient.synedrion_review: 固有名詞 `synedrion` で始まっています。`execute_synedrion_review` や `perform_synedrion_review` とすべきです。(Medium)
- main: 名詞です。エントリーポイントとしての慣習ですが、厳密には `run_main` 等の動詞が規則に適合します。(Low)
- close_after (in `_request`): 変数名が動詞句（命令）のように読めます。状態を表す形容詞的命名（例: `should_close`）や名詞（例: `auto_close_enabled`）が適切です。(Medium)
- retry_after (in `_request`): 変数名が動詞句（命令）のように読めます。名詞 `retry_delay` が適切です。(Medium)

## 重大度
Medium
