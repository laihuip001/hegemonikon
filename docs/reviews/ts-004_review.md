# テスト速度の時計師 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `poll_session` メソッド内で `asyncio.sleep` を使用しており、テスト時の待機時間が長くなる要因となっている。
- `with_retry` デコレータ内で `asyncio.sleep` を使用しており、リトライ発生時にテスト時間が延びる。
- 外部API (`https://jules.googleapis.com/v1alpha`) への直接的な依存があり、テストがネットワーク状況やAPIの応答速度に左右される。
- 関連する統合テスト（`test_create_task.py`, `test_parallel.py`）は、APIキーが必要なためスキップされるが、実行時はポーリングにより30秒以上かかる設計となっている。

## 重大度
Medium
