# デッドコード検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **`JulesClient._session` プロパティ (L176-179)**:
  - 内部メソッド `_request` 等では `_shared_session` や `_owned_session` を直接参照しており、このプロパティはクラス内で一度も使用されていない。
  - プロパティにアクセスした場合、毎回新しい `aiohttp.ClientSession()` を生成して返すが、これをクローズする機構がなく、誤って使用すると重大なリソースリーク（CWE-772）を引き起こす可能性がある。
- **`with_retry` デコレータ内の到達不能コード (L146)**:
  - `raise last_exception` は `for` ループの後に配置されているが、ループの最終回で必ず例外が再送出されるため、この行には通常到達しない。
  - `max_attempts` が 0 の場合のみ到達するが、その場合は `last_exception` が `None` のため `TypeError` となる。
- **`JulesResult.is_failed` プロパティ (L110-112)**:
  - 定義されているが、`synedrion_review` メソッドなどでは `len(all_results) - succeeded` のように計算しており、このプロパティは活用されていない。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
