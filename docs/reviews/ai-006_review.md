# DRY違反検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- Jules APIへの接続ロジック（ベースURL、ヘッダー生成、`aiohttp`セッション管理）が、以下の3ファイル間で重複して実装されています：
  1. `mekhane/symploke/jules_client.py` (`JulesClient`クラス内)
  2. `mekhane/symploke/run_specialists.py` (`create_session`, `check_session_status`関数)
  3. `mekhane/symploke/tests/test_api_connection.py` (`test_connection`関数)
- 特に `run_specialists.py` は `JulesClient` が存在するにも関わらず、独自にAPIリクエスト処理を再実装しており、API仕様変更時の保守性を低下させています。
- `test_api_connection.py` も `JulesClient` をインポートしていますが、実際の接続テストでは独自のHTTPリクエストロジックを使用しています。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
