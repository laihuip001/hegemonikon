# 再試行ロジック評価者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- **ジッター（ゆらぎ）の欠如**: `with_retry` デコレータおよび `poll_session` メソッド内のバックオフ計算において、ランダムなジッターが含まれていません (`delay *= backoff_factor`, `current_interval * 2`)。これにより、複数のクライアントが同時に再試行する「サンダリング・ハード（Thundering Herd）」問題が発生するリスクがあります。
- **Retry-After ヘッダーの解析**: `_request` メソッド内で `int(retry_after)` としていますが、HTTP仕様では `Retry-After` は日付形式（HTTP-date）の場合もあります。日付形式が返された場合、`ValueError` が発生し、再試行ロジックが機能しません。
- **ポーリングのバックオフ**: `poll_session` において、レート制限時の待機時間が `min(current_interval * 2, 60)` となっていますが、ここにもジッターがありません。

## 重大度
- High

## 沈黙判定
- 発言（要改善）
