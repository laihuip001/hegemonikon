# マジックナンバー検出者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 発見事項
- Line 269: `keepalive_timeout=30` - コネクション維持時間がハードコードされている。定数化すべき。
- Line 343: `body[:200]` - ログ出力時の切り捨て長がハードコードされている。定数化すべき。
- Line 480: `consecutive_unknown >= 3` - UNKNOWN状態の許容回数がハードコードされている。定数化すべき。
- Line 493: `min(current_interval * 2, 60)` - ポーリング時のバックオフ上限(60)と係数(2)がハードコードされている。定数化すべき。
- Line 727: `min_length = visible_chars * 2 + 4` - マスキング時の最小長計算におけるバッファ値(4)がハードコードされている。

## 重大度
- Medium

## 沈黙判定
- 発言（要改善）
