# コンテキスト喪失検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **`get_session` におけるコンテキストの不完全な再構築**: `get_session` メソッドは API レスポンスのみから `JulesSession` オブジェクトを新規作成しています (`prompt=data.get("prompt", "")`)。もし `GET /sessions/{id}` の API レスポンスがプロンプトやソースの完全な情報を含まない場合（軽量なステータス確認用レスポンスなど）、返却されるオブジェクトでは元のコンテキスト（prompt, source）が空文字やデフォルト値になり、消失します。
- **未知のステータスの曖昧化**: `parse_state` 関数は認識できないステータス文字列をすべて `SessionState.IN_PROGRESS` ("likely active") にマッピングしています。これにより、API が将来的に追加するかもしれない重要なステータス（例: `WAITING_FOR_INPUT`, `CANCELLED`, `QUOTA_EXCEEDED`）の文脈が失われ、クライアントが誤ってポーリングを継続する原因となります。
- **出力アーティファクトの限定的な取得**: `get_session` は `outputs` リストの最初の要素 (`outputs[0]`) のみをチェックして Pull Request URL を取得しています。セッションが複数の出力を生成する場合や、PR が最初の出力でない場合、それらの成果物に関するコンテキストが無視され、呼び出し元に伝わりません。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
