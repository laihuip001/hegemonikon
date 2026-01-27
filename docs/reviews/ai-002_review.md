# 専門家レビュー: Mapping ハルシネーション検出者

## 分析対象
`mekhane/symploke/jules_client.py`

## 発見事項
`mekhane/symploke/jules_client.py` は、`https://jules.googleapis.com/v1alpha` というベースURLを持つ "Google Jules API" と対話するクライアントライブラリとして実装されています。しかし、以下の点において重大なハルシネーション（Mapping Hallucination）が確認されました。

1.  **存在しないAPIエンドポイント**: Google Cloud Platform等の公式ドキュメントにおいて、"Google Jules API" という名称のサービスは存在しません。また、`jules.googleapis.com` というホスト名も公に解決可能なDNSレコードを持ちません。
2.  **架空のメソッド呼び出し**: コード内で呼び出されている `POST /sessions` (セッション作成) や `GET /sessions/{session_id}` (ポーリング) は、実在しない仕様に基づいています。
3.  **無効な実装**: このクライアントを使用するコード（`run_specialists.py`, `jules_mcp_server.py` 等）は、実在しないサーバーに接続を試みるため、全てDNS解決エラーまたは接続エラーで失敗します。

## 重大度
**高 (High)**

## 推奨事項
1.  **コードの即時無効化または削除**: 現在の `JulesClient` は機能しないため、依存するコンポーネントを含めて削除するか、使用を停止する必要があります。
2.  **代替サービスへの移行**: 本来意図していた機能（AIによるコード生成やタスク実行と推測されます）を実現するために、実在するサービス（例: Google Vertex AI Agent Builder, Cloud Build, GitHub Copilot API 等）を利用する実装に置き換えてください。
3.  **依存箇所の洗い出し**: `grep` 等を使用して `JulesClient` を参照している箇所を特定し、修正計画を立ててください。

## 沈黙判定
**発言 (Speak)**
