# finally見張り番 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- `get_boot_context` 関数内の `urllib.request.urlopen(req, timeout=5)` がリソース（ソケット）を返していますが、closeされていません。`with` 文または `finally` ブロックを使用して確実に解放する必要があります。(High)

## 重大度
High
