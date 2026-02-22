# Unicode警戒者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言

## 発見事項
- **文字列スライスの危険性**: `summary[:50]` (L132), `content[:200]` (L219), `summary[:100]` (L432) などの単純なスライスは、サロゲートペアや結合文字（emoji, ZWJ sequence）の途中で切断し、不正な文字（豆腐文字）を生む可能性がある。`grapheme cluster` を考慮した切断が必要。
- **len() の不正確さ**: `len(summary) > 50` (L131) や `len(content)` (L522) は、見た目の文字数ではなくコードポイント数を返すため、結合文字や絵文字（例: 👨‍👩‍👧‍👦 は1文字に見えて複数コードポイント）を含む場合に意図しない挙動となる。
- **Unicode正規化の欠如**: 外部入力（ファイル読み込み、引数）に対して `unicodedata.normalize` が行われていないため、NFC/NFD の違いによる比較不整合のリスクがある。

## 重大度
Low
