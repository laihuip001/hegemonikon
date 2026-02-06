# Optional浄化者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `JulesResult` クラスにおいて `session` および `error` フィールドが `Optional` で定義されており、結果の成否を `None` の有無で判断している (Medium)。
  - `None` を返す可能性のあるフィールドによって、利用側で `None` チェックが強制される。
  - `Result` 型（Success/Failure）や多態性を用いて、存在の有無ではなく「状態」として表現すべき。
- `JulesSession` クラスの `pull_request_url`, `error`, `error_type` が `Optional` で定義されている (Medium)。
  - 不在を `None` で表現しており、空オブジェクトや特定の型状態による表現が検討されていない。

## 重大度
Medium
