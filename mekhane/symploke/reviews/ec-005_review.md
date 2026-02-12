# Unicode警戒者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `mask_api_key`関数内での`len()`による長さ判定: Unicode結合文字や絵文字を含む場合、見た目の長さと一致しない可能性がある (Low)
- `mask_api_key`関数内でのスライス操作: サロゲートペアや結合文字の途中で切断される可能性がある (Low)
- `_request`メソッド内でのログ出力時のスライス(`body[:200]`): マルチバイト文字の途中で切断され、不正なUnicodeシーケンスとしてログに出力される可能性がある (Low)
- Unicode正規化(`unicodedata.normalize`)の欠如: 異なる正規化形式(NFC/NFD)の同一文字列が別物として扱われる可能性がある (Low)

## 重大度
Low
