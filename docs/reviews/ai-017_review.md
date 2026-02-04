# マジックナンバー検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- `keepalive_timeout=30` (L164): TCP接続のキープアライブ時間がハードコードされています。
- `body[:200]` (L226): エラーログのレスポンスボディ切り出し長が説明なくハードコードされています。
- `consecutive_unknown >= 3` (L349): UNKNOWN状態の連続許容回数がハードコードされています。
- `min(current_interval * 2, 60)` (L361): ポーリングのバックオフ上限(60秒)がハードコードされています。
- `visible_chars * 2 + 4` (L519): APIキーマスク処理のパディング長がハードコードされています。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
