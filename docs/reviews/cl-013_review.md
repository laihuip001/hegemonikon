# エラーハンドリング一貫性評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **不統一な例外ラップ**: `create_session` と `get_session` は429エラーに対して `RateLimitError` を送出するが、その他のHTTPエラーは `aiohttp.ClientResponseError` としてそのまま送出している。統一された例外階層（例: `JulesAPIError`）が望ましい。
- **JSONパースエラーの未処理**: `await resp.json()` が `try/except` なしで呼び出されている。非JSONのエラーレスポンス（500エラーやプロキシエラーなど）の場合、`aiohttp.ContentTypeError` が発生し、実際のレスポンス内容が隠蔽される可能性がある。
- **ネットワークエラーハンドリングの欠如**: `poll_session` 内で `aiohttp.ClientError`（接続断など）がハンドリングされていない。一時的なネットワーク障害で長時間のポーリングが中断される恐れがある。
- **`parse_state` における沈黙の失敗**: `parse_state` は `ValueError` 発生時に `IN_PROGRESS` をデフォルトとして返すが、APIの仕様変更で未知のステータスが返された場合、実際には完了しているのに無限にポーリングし続ける可能性がある。
- **バッチ実行時のエラーオブジェクト**: `batch_execute` はエラー時にダミーの `JulesSession` オブジェクトを生成している。実用上は便利だが、正常なセッションとエラープレースホルダーが混在しており、明示的な `Result` 型や `is_error` フラグの使用が検討されるべきである。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
