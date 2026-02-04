# エラーメッセージ評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **`_request` メソッドの `raise_for_status()`**: `aiohttp.ClientResponseError` がそのまま送出されるため、APIが返す詳細なエラーメッセージ（JSON body等）が例外メッセージに含まれず、ユーザーにとって原因特定が困難になる可能性がある。エラーログは出力されているが、例外オブジェクト自体に情報を含める方が親切である。
- **エラーログの切り詰め**: `_request` 内で `logger.error(f"API error {resp.status}: {body[:200]}")` としているが、200文字ではネストされたJSONエラー情報の重要な部分（`message` や `details` など）が切れる恐れがある。
- **`TimeoutError` の情報不足**: `poll_session` でタイムアウトした際、どのステータスで止まっていたかがメッセージに含まれていない。「PLANNINGで止まっている」のか「TESTINGで止まっている」のかでユーザーの対応が変わるため、最終ステータスを含めるとより共感的である。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
