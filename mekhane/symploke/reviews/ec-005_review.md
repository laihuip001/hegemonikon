# Unicode警戒者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- mask_api_key関数: len(key) による長さ判定と key[:visible_chars] などのスライス操作があり、サロゲートペアや結合文字が含まれる場合に文字が破壊されるリスクがある (Low)
- _requestメソッド: ログ出力時に body[:200] としており、マルチバイト文字の境界で切断され、末尾の文字が破壊される可能性がある (Low)
- synedrion_reviewメソッド: domains や axes のフィルタリングにおいて Unicode 正規化 (NFC/NFD) が行われておらず、見た目が同じでもバイト列が異なる場合にマッチしない可能性がある (Low)

## 重大度
Low
