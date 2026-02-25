# Unicode警戒者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言

## 発見事項
- **Naive string slicing**:
  - Line 132: `summary[:50]`
  - Line 223: `content[:200]`
  - Line 474: `summary[:100]`
  Unicode文字列に対するスライスは、サロゲートペアや結合文字シーケンスの途中で切断されるリスクがあり、文字化けの原因となる可能性がある。

- **Naive length check**:
  - Line 131: `if len(summary) > 50:`
  `len()` はコードポイント数を返すため、結合文字や絵文字を含む文字列（書記素クラスター）の「見た目の長さ」と一致しない場合がある。

- **Missing Unicode Normalization**:
  - 入力テキスト（ファイル読み込みや引数）に対して `unicodedata.normalize` が行われていないため、見た目が同じでもバイト列表現が異なる文字列（NFC vs NFD）が混在する可能性がある。

## 重大度
Low
