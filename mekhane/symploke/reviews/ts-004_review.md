# テスト速度の時計師 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **同期的なネットワーク呼び出し (Medium)**: `boot_integration.py` の `get_boot_context` 内で `urllib.request.urlopen` を使用して n8n Webhook を呼び出しています (L422-432)。5秒のタイムアウトが設定されていますが、同期的にブロックするため、ネットワーク遅延時にテストや実行全体の速度を低下させる可能性があります。
- **重いスレッドプールタイムアウト (Medium)**: `boot_axes.py` に委譲された軸ロード処理 (`load_sophia`, `load_pks`, `load_attractor` 等) で `ThreadPoolExecutor` が使用されていますが、タイムアウト値が最大 30秒 (`load_attractor`) と長く設定されています。並列化されていますが、全体としての待機時間が長くなるリスクがあります。特に `load_attractor` (L237) の 30秒、`load_sophia` (L69) の 15秒はテスト実行時のボトルネックになり得ます。

## 重大度
Medium
