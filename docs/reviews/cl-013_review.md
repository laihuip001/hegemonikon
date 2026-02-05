# エラーハンドリング一貫性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **戻り値パターンの不一致**: `batch_execute` は例外を捕捉して `JulesResult` オブジェクト（Result Pattern）を返しますが、`create_session` や `poll_session` などの単体操作メソッドは例外をそのまま送出します（Exception Pattern）。利用者は単体実行かバッチ実行かによって異なるエラー処理ロジックを実装する必要があります。
- **実装詳細の漏洩**: `_request` メソッドおよびそれを使用する各メソッドは、`aiohttp.ClientResponseError` や `aiohttp.ClientError` を捕捉・ラップせずにそのまま送出しています。これにより、呼び出し元は `aiohttp` に依存したエラー処理を記述する必要があり、カプセル化が破壊されています。
- **タイムアウト例外の不統一**: `poll_session` メソッドは標準の `TimeoutError` を送出しますが、HTTP通信のタイムアウトが発生した場合は `aiohttp` 由来の例外が発生する可能性があります。例外型が統一されていません。
- **エラー情報のコンテキスト喪失**: `_request` メソッド内で `resp.raise_for_status()` を使用しているため、APIが返す詳細なエラーメッセージがログには出力されるものの、送出される例外オブジェクト自体には含まれにくい構造になっています。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
