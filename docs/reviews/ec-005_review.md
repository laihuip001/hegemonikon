# Unicode警戒者 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- `mask_api_key` 関数における `len()` とスライス処理は、サロゲートペアや結合文字（例: 絵文字、アクセント記号付き文字）を考慮していません。書記素クラスター（Grapheme Clusters）の途中で切断される可能性があります。(Low)
- エラーログ出力時の `body[:200]` は、マルチバイト文字や結合文字の途中で切断し、無効なUnicodeシーケンスをログに残す可能性があります。(Low)
- `create_session` 等の入力文字列に対して `unicodedata.normalize` による正規化が行われていません。見た目が同じでもバイト列が異なる文字がそのままAPIに送信されます。(Low)

## 重大度
Low
