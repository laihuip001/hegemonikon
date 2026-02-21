# Unicode警戒者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言

## 発見事項
- Line 142: `summary[:50]` によるナイーブな文字列切り出し。書記素クラスタ（Grapheme Cluster）を破壊し、結合文字やEmojiシーケンスが不正になるリスクがある。 (Medium)
- Line 245: `content[:200]` によるコンテキスト切り出し。同上のリスク。 (Medium)
- Line 534: `summary[:100]` によるサマリー切り出し。同上のリスク。 (Medium)
- `len()` を用いた文字数カウント（Line 142, 475等）は、サロゲートペアや結合文字、Emojiの視覚的な幅や「文字数」と乖離する。 (Low)
- 外部入力（ファイル読み込み）に対する `unicodedata.normalize` の欠如。 (Low)

## 重大度
Low
