# import順序の典礼官 レビュー

## 対象ファイル
`mekhane/symploke/jules_client.py`

## 判定
発言（要改善）

## 発見事項
- stdlibセクションにthird-partyライブラリ(`aiohttp`)が混入している (Medium)
- stdlibセクション内でアルファベット順が守られていない (`random` が `uuid` の後にある) (Medium)
- stdlibとthird-partyの間に空行による分離がない (Medium)

## 重大度
Medium
