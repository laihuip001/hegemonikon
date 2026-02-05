# デッドコード検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **到達不能コード (`with_retry` デコレータ)**: `with_retry` 内部関数のループ終了後にある `raise last_exception` は、ループ内（最終試行時）で必ず例外が再送出されるか、正常終了時にリターンされるため、論理的に到達不能なコード（Dead Code）となっています。
- **バグによる到達不能コード (`create_session`)**: `create_session` メソッドにおいて、`JulesSession` 初期化時に必須引数 `source` が渡されていません。これにより実行時に必ず `TypeError` が発生し、直後の `return` 文が到達不能となっています。
- **バグによる到達不能コード (`poll_session`)**: `poll_session` メソッドにおいて、`UnknownStateError` を送出する際に必須引数 `session_id` が渡されていません。これにより意図した例外処理コードが機能せず、`TypeError` が発生します。
- **非推奨コードの残留 (`parse_state`)**: `parse_state` 関数は "Legacy alias" とコメントされていますが、`create_session` および `get_session` 内部で依然として使用されています。`SessionState.from_string` への置き換えが行われておらず、将来的に不要となるコードが残存しています。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）
