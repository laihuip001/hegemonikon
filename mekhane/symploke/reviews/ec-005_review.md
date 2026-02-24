# Unicode警戒者 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言

## 発見事項
- **`_load_projects` (Line 123)**: `summary[:50]`
  - `len(summary)` で文字数をカウントしており、サロゲートペアや結合文字（例: 👨‍👩‍👧‍👦）が分断される可能性があります。
- **`get_boot_context` (Line 207)**: `content[:200]`
  - Handoff のコンテンツは自然言語であり、絵文字を含む可能性が高いため、単純なスライスは危険です。
- **`generate_boot_template` (Line 512)**: `summary[:100]`
  - ここでも `summary` を単純にスライスしており、Unicode 文字が破損するリスクがあります。
- **Unicode正規化の欠如**
  - 入力文字列に対する `unicodedata.normalize('NFC', ...)` 等の処理が見当たりません。

## 重大度
Low
